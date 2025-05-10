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
    return render_template('home.html')

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
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('view_blog'))
        
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            return render_template('register.html')
        
        if len(password) < 6:
            return render_template('register.html')
        
        # Default role is subscriber
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
            return redirect(url_for('view_blog'))
        else:
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

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
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard homepage"""
    return render_template('admin/dashboard.html')

@app.route('/admin/blog-analytics')
def blog_analytics():
    """Blog post analytics"""
    analytics = Post.get_analytics()
    
    # Filter sensitive information for non-admin users
    if not session.get('user_id') or session.get('role') != 'admin':
        # Remove sensitive fields or modify data as needed
        for post in analytics:
            # Remove details that should be admin-only
            if 'ip_addresses' in post:
                del post['ip_addresses']
    
    return render_template('admin/blog_analytics.html', analytics=analytics)

@app.route('/admin/cv-analytics')
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
    
    return render_template('admin/cv_analytics.html', analytics=analytics)

@app.route('/admin/visitor-analytics')
def visitor_analytics():
    """Visitor statistics"""
    analytics = VisitorStat.get_analytics()
    
    # Filter sensitive information for non-admin users
    if not session.get('user_id') or session.get('role') != 'admin':
        # Remove IP addresses or other sensitive data
        pass  # Specific filtering based on what's in the analytics
    
    return render_template('admin/visitor_analytics.html', analytics=analytics)

@app.route('/admin/user-analytics')
def user_analytics():
    """User statistics"""
    analytics = User.get_analytics()
    
    # Handle case when analytics is None
    if analytics is None:
        # Provide default empty analytics data
        analytics = {
            'total_users': 0,
            'by_role': [],
            'recent_users': [],
            'all_users': []
        }
    
    # Filter sensitive information for non-admin users
    if not session.get('user_id') or session.get('role') != 'admin':
        # For non-admins, only show summary statistics but not user details
        if 'all_users' in analytics:
            # Remove email addresses and only show limited information
            for user in analytics['all_users']:
                user['email'] = '***@***.***'  # Mask email addresses
    
    return render_template('admin/user_analytics.html', analytics=analytics)

@app.route('/api/notifications')
def get_notifications():
    """API endpoint to get recent notifications"""
    # Filter sensitive notifications for non-admins
    if not session.get('user_id') or session.get('role') != 'admin':
        # Get notifications but filter out sensitive ones
        notifications = Notification.get_recent(10)
        # Could add additional filtering if needed
    else:
        notifications = Notification.get_recent(10)
    
    return jsonify(notifications)

if __name__ == '__main__':
    app.run(debug=True) 