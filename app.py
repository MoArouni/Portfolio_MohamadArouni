from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, send_from_directory
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import User, Post, Comment, BlogLike, CommentLike, CVDownload, VisitorStat, Notification
from db_init import get_db_connection, init_db
from functools import wraps
import math

# Configure app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_blog')

# Custom template filter for newlines to <br>
@app.template_filter('nl2br')
def nl2br(s):
    return s.replace('\n', '<br>')

# Initialize database if it doesn't exist
if not os.path.exists('blog.db'):
    init_db()

# Authorization decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    g.user = None
    user_id = session.get('user_id')
    if user_id:
        g.user = User.get_by_id(user_id)
    
    # Track page views for analytics, excluding static files and admin pages
    if not request.path.startswith('/static') and not request.path.startswith('/admin'):
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        visitor_id = VisitorStat.record_visit(ip, request.path)
        
        # Check for view count milestones (every 100 views)
        if visitor_id:
            conn = get_db_connection()
            total_views = conn.execute('SELECT COUNT(*) as count FROM visitor_stats').fetchone()['count']
            conn.close()
            
            if total_views % 100 == 0:
                Notification.create_view_milestone_notification(total_views)

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

# Routes
@app.route('/')
def home():
    # Get the latest blog posts
    latest_posts = Post.get_latest(2)
    
    # Get comments and like count for each post
    for post in latest_posts:
        post['comments'] = Comment.get_for_post(post['id'])
        post['like_count'] = BlogLike.get_count_for_post(post['id'])
        
    return render_template('home.html', latest_posts=latest_posts)

@app.route('/blog')
def view_blog():
    # Get month filter from query params
    filter_month = request.args.get('month', None)
    
    # Get posts with filter
    posts = Post.get_all(filter_month)
    
    # Get available months for filter dropdown
    available_months = Post.get_available_months()
    
    # For each post, get its comments and like count
    for post in posts:
        post['comments'] = Comment.get_for_post(post['id'])
        post['like_count'] = BlogLike.get_count_for_post(post['id'])
        
        # Check if current user has liked this post
        if g.user:
            post['user_has_liked'] = BlogLike.has_user_liked(post['id'], g.user['id'])
        else:
            post['user_has_liked'] = False
    
    # If a specific post is highlighted in the query parameters, increment its view count
    highlighted_post_id = request.args.get('post_id')
    if highlighted_post_id and highlighted_post_id.isdigit():
        Post.increment_view_count(int(highlighted_post_id))
    
    return render_template('view_blog.html', posts=posts, 
                          available_months=available_months,
                          filter_month=filter_month)

@app.route('/blog/post/<int:post_id>')
def view_post(post_id):
    # Get the post
    post = Post.get_by_id(post_id)
    if not post:
        return redirect(url_for('view_blog'))
    
    # Increment view count
    Post.increment_view_count(post_id)
    
    # Get comments and like count
    post['comments'] = Comment.get_for_post(post['id'])
    post['like_count'] = BlogLike.get_count_for_post(post['id'])
    
    # Check if current user has liked this post
    if g.user:
        post['user_has_liked'] = BlogLike.has_user_liked(post['id'], g.user['id'])
    else:
        post['user_has_liked'] = False
    
    return render_template('view_blog.html', posts=[post], single_post=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.authenticate(email, password)
        
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # For AJAX requests, return a success indicator
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if user['role'] == 'admin':
                    return jsonify({'success': True, 'redirect': url_for('admin_dashboard', auth_event='login', username=user['username'])})
                else:
                    return jsonify({'success': True, 'redirect': url_for('view_blog', auth_event='login', username=user['username'])})
            else:
                # For regular form submissions, redirect as before
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard', auth_event='login', username=user['username']))
                else:
                    return redirect(url_for('view_blog', auth_event='login', username=user['username']))
    
        # Handle failed login
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Invalid email or password'})
        else:
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Field validation
        errors = {}
        if not username:
            errors['username'] = 'Username is required'
        elif len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters'
            
        if not email:
            errors['email'] = 'Email is required'
            
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters'
            
        # Check if username or email already exists
        if not errors:
            if User.exists_with_username(username):
                errors['username'] = 'Username already taken'
            if User.exists_with_email(email):
                errors['email'] = 'Email already registered'
        
        # If there are validation errors
        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'errors': errors})
            else:
                return render_template('register.html', errors=errors)
        
        # Create user
        user_id = User.create(username, email, password)
        
        if user_id:
            # Create notification for new user
            Notification.create_new_user_notification(username)
            
            # Log the user in directly
            user = User.get_by_id(user_id)
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # Return success response or redirect
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('view_blog', auth_event='login', username=username)})
        else:
                return redirect(url_for('view_blog', auth_event='login', username=username))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home', auth_event='logout'))

@app.route('/add', methods=['GET'])
@login_required
@admin_required
def add_entry():
    return render_template('add_entry.html')

@app.route('/add', methods=['POST'])
@login_required
@admin_required
def add_post():
    title = request.form['title']
    content = request.form['content']
    
    if not title or not content:
        return redirect(url_for('add_entry'))
    
    Post.create(title, content, session['user_id'])
    return redirect(url_for('view_blog'))

@app.route('/delete/<int:post_id>')
@login_required
@admin_required
def delete_post(post_id):
    Post.delete(post_id)
    return redirect(url_for('view_blog'))

@app.route('/edit/<int:post_id>', methods=['GET'])
@login_required
@admin_required
def edit_post(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        return redirect(url_for('view_blog'))
    return render_template('edit_post.html', post=post)

@app.route('/update/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def update_post(post_id):
    title = request.form['title']
    content = request.form['content']
    
    if not title or not content:
        return redirect(url_for('edit_post', post_id=post_id))
    
    Post.update(post_id, title, content)
    return redirect(url_for('view_blog'))

@app.route('/comment', methods=['POST'])
@login_required
def add_comment():
    post_id = request.form['post_id']
    content = request.form['content']
    
    if not content:
        return redirect(url_for('view_blog'))
    
    Comment.create(post_id, content, session['user_id'])
    
    # Create notification
    post = Post.get_by_id(post_id)
    if post:
        Notification.create_comment_notification(session['username'], False, post['title'])
    
    return redirect(url_for('view_blog') + '#post-' + post_id)

@app.route('/anonymous_comment', methods=['POST'])
def add_anonymous_comment():
    post_id = request.form['post_id']
    content = request.form['content']
    author_name = request.form.get('author_name', 'Anonymous')
    
    if not content:
        return redirect(url_for('view_blog'))
    
    Comment.create_anonymous(post_id, content, author_name)
    
    # Create notification
    post = Post.get_by_id(post_id)
    if post:
        Notification.create_comment_notification(author_name, True, post['title'])
    
    return redirect(url_for('view_blog') + '#post-' + post_id)

@app.route('/delete/comment/<int:comment_id>')
@login_required
@admin_required
def delete_comment(comment_id):
    Comment.delete(comment_id)
    return redirect(url_for('view_blog'))

# New routes for additional features

@app.route('/post/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    """Add a like to a blog post"""
    # Check if the post exists
    post = Post.get_by_id(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    # Get the user info if logged in
    user_id = session.get('user_id')
    username = session.get('username')
    is_anonymous = not user_id
    
    # Store like
    like_id = BlogLike.create(post_id, user_id, username, is_anonymous)
    
    # If like was successful, return success
    if like_id:
        # Create notification
        Notification.create_post_like_notification(username, is_anonymous, post['title'])
        
        # Get updated like count
        like_count = BlogLike.get_count_for_post(post_id)
        return jsonify({'success': True, 'like_count': like_count})
    else:
        # User may have already liked this post
        return jsonify({'success': False, 'error': 'Already liked'}), 400

@app.route('/post/anonymous_like/<int:post_id>', methods=['POST'])
def anonymous_like_post(post_id):
    """Add an anonymous like to a blog post"""
    # Check if the post exists
    post = Post.get_by_id(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post not found'}), 404
    
    # Get the data from the request
    data = request.get_json()
    username = data.get('username', 'Anonymous')
    anonymous_id = data.get('anonymous_id', '')
    
    # Additional metadata
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    # Try to store the anonymous like
    like_id = BlogLike.create_anonymous(post_id, username, anonymous_id, ip)
    
    # If like was successful, return success
    if like_id:
        # Create notification
        Notification.create_post_like_notification(username, True, post['title'])
        
        # Get updated like count
        like_count = BlogLike.get_count_for_post(post_id)
        return jsonify({'success': True, 'like_count': like_count})
    else:
        # Error creating like or already liked
        return jsonify({'success': False, 'error': 'Already liked'}), 400

@app.route('/post/unlike/<int:post_id>', methods=['POST'])
@login_required
def unlike_post(post_id):
    """Remove a user's like from a blog post"""
    user_id = session.get('user_id')
    
    # Try to delete the like
    success = BlogLike.delete(post_id=post_id, user_id=user_id)
    
    if success:
        # Get updated like count
        like_count = BlogLike.get_count_for_post(post_id)
        return jsonify({'success': True, 'like_count': like_count})
    else:
        return jsonify({'success': False, 'error': 'Like not found'}), 404

@app.route('/comment/like/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    """Add a like to a comment"""
    user_id = session.get('user_id')
    username = session.get('username')
    
    # Add the like
    like_id = CommentLike.create(comment_id, user_id)
    
    if like_id:
        # Get the post info for notification
        conn = get_db_connection()
        comment_info = conn.execute('''
            SELECT c.post_id, p.title 
            FROM comments c
            JOIN posts p ON c.post_id = p.id
            WHERE c.id = ?
        ''', (comment_id,)).fetchone()
        conn.close()
        
        if comment_info:
            # Create notification
            Notification.create_comment_like_notification(username, False, comment_info['title'])
        
        # Get updated like count
        like_count = CommentLike.get_count_for_comment(comment_id)
        return jsonify({'success': True, 'like_count': like_count})
    else:
        return jsonify({'success': False, 'error': 'Already liked or comment not found'}), 400

@app.route('/comment/unlike/<int:comment_id>', methods=['POST'])
@login_required
def unlike_comment(comment_id):
    """Remove a like from a comment"""
    user_id = session.get('user_id')
    
    # Delete the like
    success = CommentLike.delete(comment_id, user_id)
    
    if success:
        # Get updated like count
        like_count = CommentLike.get_count_for_comment(comment_id)
        return jsonify({'success': True, 'like_count': like_count})
    else:
        return jsonify({'success': False, 'error': 'Like not found'}), 404

@app.route('/comment/author-like/<int:comment_id>', methods=['POST'])
@login_required
@admin_required
def toggle_author_like(comment_id):
    """Toggle the 'liked by author' status of a comment"""
    # Get current status
    conn = get_db_connection()
    comment = conn.execute('SELECT liked_by_author FROM comments WHERE id = ?', 
                          (comment_id,)).fetchone()
    conn.close()
    
    if not comment:
        return jsonify({'success': False, 'error': 'Comment not found'}), 404
    
    # Toggle the status
    new_status = not bool(comment['liked_by_author'])
    success = Comment.toggle_author_like(comment_id, new_status)
    
    if success:
        return jsonify({'success': True, 'liked_by_author': new_status})
    else:
        return jsonify({'success': False, 'error': 'Update failed'}), 500

@app.route('/download_cv', methods=['POST'])
def download_cv():
    """Record CV download analytics and serve the file"""
    # Get reason from either form data or JSON
    if request.is_json:
        data = request.get_json()
        reason = data.get('reason', 'Not specified')
    else:
        reason = request.form.get('reason', 'Not specified')
    
    # Get user info if logged in
    user_id = session.get('user_id')
    username = session.get('username', 'Anonymous')
    is_anonymous = not user_id
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    
    # Record the download
    CVDownload.create(reason, user_id, ip)
    
    # Create notification
    Notification.create_cv_download_notification(username, is_anonymous, reason)
    
    # Serve the CV file
    return send_from_directory('static/pdf', 'Mohamad_Arouni_CV.pdf')

# Admin dashboard routes
@app.route('/analytics')
def admin_dashboard():
    """Admin dashboard homepage"""
    return render_template('analytics/dashboard.html')

@app.route('/analytics/blog-analytics')
def blog_analytics():
    """Blog post analytics"""
    analytics = Post.get_analytics()
    
    # Get the total likes count directly from the database
    total_likes_count = BlogLike.get_total_likes_count()
    
    # Filter sensitive information for non-admin users
    if not session.get('user_id') or session.get('role') != 'admin':
        # Remove sensitive user information
        for post in analytics:
            # Remove details that should be admin-only
            if 'ip_addresses' in post:
                del post['ip_addresses']
            if 'username' in post:
                post['username'] = 'Anonymous'
            if 'email' in post:
                post['email'] = '***@***.***'
    
    return render_template('analytics/blog_analytics.html', analytics=analytics, total_likes_count=total_likes_count)

@app.route('/analytics/cv-analytics')
def cv_analytics():
    """CV download analytics"""
    analytics = CVDownload.get_analytics()
    
    # Filter sensitive information for non-admin users
    if not session.get('user_id') or session.get('role') != 'admin':
        # Remove personally identifiable information
        if 'recent' in analytics:
            for item in analytics['recent']:
                # Mask or remove sensitive fields
                if 'ip_address' in item:
                    del item['ip_address']
                if 'username' in item:
                    item['username'] = 'Anonymous'
                if 'email' in item:
                    item['email'] = '***@***.***'
    
    return render_template('analytics/cv_analytics.html', analytics=analytics)

@app.route('/analytics/visitor-analytics')
def visitor_analytics():
    """Visitor statistics"""
    analytics = VisitorStat.get_analytics()
    
    # Filter sensitive information for non-admin users
    if not session.get('user_id') or session.get('role') != 'admin':
        # Remove IP addresses or other sensitive data
        pass  # Specific filtering based on what's in the analytics
    
    return render_template('analytics/visitor_analytics.html', analytics=analytics)

@app.route('/analytics/user-analytics')
@login_required
@admin_required
def user_analytics():
    """User statistics"""
    # Get fresh data directly from the database to ensure accuracy
    conn = get_db_connection()
    
    # Get total users count
    result = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
    total_users = result['count'] if result else 0
    
    # Get users by role
    by_role_query = '''
        SELECT role, COUNT(*) as count 
        FROM users 
        GROUP BY role 
        ORDER BY count DESC
    '''
    by_role = conn.execute(by_role_query).fetchall()
    
    # First check which columns exist in the users table
    table_info = conn.execute("PRAGMA table_info(users)").fetchall()
    columns = [col['name'] for col in table_info]
    
    # Get all users for the table view with most recent first
    # Determine if created_at exists, otherwise use registration_date or id as fallback
    if 'created_at' in columns:
        order_by = 'created_at DESC'
        all_users_query = f'''
            SELECT id, username, email, role, created_at 
            FROM users 
            ORDER BY {order_by}
        '''
    else:
        # Fallback to ordering by ID if created_at doesn't exist
        order_by = 'id DESC'
        all_users_query = f'''
            SELECT id, username, email, role
            FROM users 
            ORDER BY {order_by}
        '''
    
    all_users = conn.execute(all_users_query).fetchall()
    all_users_list = [dict(u) for u in all_users] if all_users else []
    
    # If created_at doesn't exist in the result, add a placeholder
    if all_users_list and 'created_at' not in all_users_list[0]:
        for user in all_users_list:
            user['created_at'] = 'Not recorded'
    
    # Build the analytics dictionary
    analytics = {
        'total_users': total_users,
        'by_role': [dict(r) for r in by_role] if by_role else [],
        'all_users': all_users_list
    }
    
    conn.close()
    
    return render_template('analytics/user_analytics.html', analytics=analytics)

@app.route('/api/notifications')
def get_notifications():
    """API endpoint to get recent notifications"""
    notifications = Notification.get_recent(5)  # Limit to 5 notifications
    
    # Filter sensitive information for non-admins
    if not session.get('user_id') or session.get('role') != 'admin':
        for notification in notifications:
            # Replace usernames with 'Anonymous' for non-admins
            if not notification['is_anonymous']:
                # Keep the notification but anonymize the username if it's a registered user
                notification['message'] = notification['message'].replace(notification['username'], 'Anonymous User')
                notification['username'] = 'Anonymous'
    
    return jsonify(notifications)

@app.route('/notifications-history')
def notifications_history():
    """Full notifications history page"""
    notifications = Notification.get_recent(50)  # Get more notifications for the history page
    
    # Filter sensitive information for non-admins
    if not session.get('user_id') or session.get('role') != 'admin':
        for notification in notifications:
            # Replace usernames with 'Anonymous' for non-admins
            if not notification['is_anonymous']:
                # Keep the notification but anonymize the username if it's a registered user
                notification['message'] = notification['message'].replace(notification['username'], 'Anonymous User')
                notification['username'] = 'Anonymous'
    
    return render_template('notifications_history.html', notifications=notifications)

if __name__ == '__main__':
    app.run(debug=True) 