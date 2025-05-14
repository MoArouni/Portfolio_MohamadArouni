from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, send_from_directory
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import User, Post, Comment, BlogLike, CommentLike, CVDownload, VisitorStat, Notification, CVVerification
from db_init import get_db_connection, init_db, create_admin_user1, db
from functools import wraps
from dotenv import load_dotenv
import math
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import re
from sqlalchemy.sql import text

# Load environment variables
load_dotenv()

# Initialize app first, before any database operations
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_blog')

# Configure app before database initialization
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres'):
    # Railway provides PostgreSQL URLs starting with postgres://
    # SQLAlchemy 1.4+ requires postgresql:// instead of postgres://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"Using PostgreSQL database at {database_url.split('@')[1] if '@' in database_url else '(redacted)'}")
else:
    # Use SQLite for local development
    sqlite_path = os.path.join(os.path.dirname(__file__), 'blog.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
    print(f"Using SQLite database at {sqlite_path} for development/testing only.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)

# Make a simple early route available even if database init fails
@app.route('/health')
def health_check():
    """Simple health check endpoint for deployment platforms that doesn't access the database"""
    try:
        # Return a simple response with no database queries
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "app_name": "Portfolio Application",
            "env": os.environ.get('FLASK_ENV', 'production')
        }), 200
    except Exception as e:
        print(f"Health check error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Database initialization will be attempted when first needed
db_initialized = False

def ensure_db_initialized():
    global db_initialized
    if db_initialized:
        return True
        
    try:
        # Check if any database tables exist by attempting a simple query
        with app.app_context():
            try:
                # Try to query users table
                db.session.execute(text('SELECT 1 FROM users LIMIT 1'))
                db_initialized = True
                print("Database already initialized")
                return True
            except Exception as e:
                print(f"Database tables not found: {e}")
                print("Attempting to initialize database...")
                
                # For PostgreSQL, use standalone init script
                if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                    from init_postgres_db import initialize_postgres_db
                    if initialize_postgres_db():
                        db_initialized = True
                        print("PostgreSQL database initialized successfully")
                        return True
                    else:
                        print("Failed to initialize PostgreSQL database")
                        return False
                        
                # For SQLite, use SQLAlchemy to create tables
                else:
                    try:
                        # Import all models to ensure they're registered with SQLAlchemy
                        from models import User, Post, Comment, BlogLike, CommentLike, CVDownload
                        
                        # Create all tables
                        db.create_all()
                        
                        # Create admin user if needed
                        from db_init import create_admin_user1
                        create_admin_user1()
                        
                        db_initialized = True
                        print("SQLite database initialized successfully")
                        return True
                    except Exception as init_error:
                        print(f"Error initializing SQLite database: {init_error}")
                        return False
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

# Configure mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')

# Initialize mail
mail = Mail(app)

# Initialize the serializer for token generation
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

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
        try:
            g.user = User.get_by_id(user_id)
        except Exception as e:
            print(f"Error loading user: {e}")
            # Don't let user loading failures break the site
            session.pop('user_id', None)
    
    # Only track page views if not an API request and not a static file
    if not request.path.startswith('/static') and not request.path.startswith('/api') and not request.path.startswith('/admin'):
        try:
            # Get IP address and clean it
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Clean up IP - many proxies add multiple IPs separated by commas
            if ip and ',' in ip:
                # Take the first IP (usually the client's real IP)
                ip = ip.split(',')[0].strip()
            
            # Truncate if too long for database
            if ip and len(ip) > 45:  # VARCHAR(45) in database
                ip = ip[:45]
            
            visitor_id = VisitorStat.record_visit(ip, request.path)
            
            # Check for view count milestones (every 100 views), but handle errors gracefully
            if visitor_id:
                try:
                    conn = get_db_connection()
                    # Use a separate transaction
                    result = conn.execute(text('SELECT COUNT(*) as count FROM visitor_stats')).fetchone()
                    
                    # Access count safely - try both mapping and index access
                    total_views = 0
                    try:
                        if hasattr(result, "_mapping"):
                            total_views = result._mapping["count"]
                        else:
                            # Try accessing by position - count is the first column
                            total_views = result[0]
                    except Exception as count_error:
                        print(f"Error accessing count: {count_error}")
                    
                    if total_views > 0 and total_views % 100 == 0:
                        try:
                            Notification.create_view_milestone_notification(total_views)
                        except Exception as notif_error:
                            print(f"Error creating milestone notification: {notif_error}")
                
                except Exception as view_error:
                    print(f"Error checking view count: {view_error}")
                    # Don't let visitor tracking break the site
        except Exception as ip_error:
            print(f"Error tracking visit: {ip_error}")
            # Don't let visitor tracking break the site

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

# Routes
@app.route('/')
def home():
    # Try to initialize the database if needed
    if not ensure_db_initialized():
        # If database initialization failed, show a simplified page
        return render_template('error.html', 
                              error_message="Database is currently unavailable. Please try again later.",
                              error_title="Database Error")
    
    try:
        # Get the latest blog posts
        latest_posts = Post.get_latest(2)
        
        # Get comments and like count for each post
        for post in latest_posts:
            post['comments'] = Comment.get_for_post(post['id'])
            post['like_count'] = BlogLike.get_count_for_post(post['id'])
        
        # Check for download parameter to trigger CV download via JS
        download_cv = request.args.get('download') == 'cv'
        error_message = request.args.get('error')
            
        return render_template('home.html', 
                              latest_posts=latest_posts, 
                              download_cv=download_cv,
                              error_message=error_message)
    except Exception as e:
        print(f"Error rendering home page: {e}")
        # Return a simplified error response
        return render_template('error.html',
                             error_message="Error loading the home page. Please try again later.",
                             error_title="Page Error")

@app.route('/blog')
def view_blog():
    # Try to initialize the database if needed
    if not ensure_db_initialized():
        # If database initialization failed, show a simplified page
        return render_template('error.html', 
                              error_message="Database is currently unavailable. Please try again later.",
                              error_title="Database Error")
    
    try:
        # Get month filter from query params
        filter_month = request.args.get('month', None)
        
        # Get posts with filter
        posts = Post.get_all(filter_month)
        
        # Get available months for filter dropdown
        available_months = Post.get_available_months()
        
        # For each post, get its comments and like count
        for post in posts:
            try:
                post['comments'] = Comment.get_for_post(post['id'])
                post['like_count'] = BlogLike.get_count_for_post(post['id'])
                
                # Check if current user has liked this post
                if g.user:
                    post['user_has_liked'] = BlogLike.has_user_liked(post['id'], g.user['id'])
                else:
                    post['user_has_liked'] = False
            except Exception as post_error:
                print(f"Error processing post {post.get('id', 'unknown')}: {post_error}")
                # Set defaults for missing data
                if 'comments' not in post:
                    post['comments'] = []
                if 'like_count' not in post:
                    post['like_count'] = 0
                post['user_has_liked'] = False
        
        # If a specific post is highlighted in the query parameters, increment its view count
        highlighted_post_id = request.args.get('post_id')
        if highlighted_post_id and highlighted_post_id.isdigit():
            try:
                Post.increment_view_count(int(highlighted_post_id))
            except Exception as view_error:
                print(f"Error incrementing view count: {view_error}")
        
        return render_template('view_blog.html', posts=posts, 
                               available_months=available_months,
                               filter_month=filter_month)
    
    except Exception as e:
        print(f"Error rendering blog page: {e}")
        # Return a simplified error response
        return render_template('error.html',
                               error_message="Error loading the blog page. Please try again later.",
                               error_title="Blog Error")

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
            # Debug prints
            print("\nLogin successful:")
            print(f"User from database - Username: {user['username']}")
            print(f"User from database - Role: {user['role']}")
            
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # Debug prints after session update
            print("\nSession after update:")
            print(f"Session username: {session.get('username')}")
            print(f"Session role: {session.get('role')}")
            
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
        comment_info = conn.execute(text('''
            SELECT c.post_id, p.title 
            FROM comments c
            JOIN posts p ON c.post_id = p.id
            WHERE c.id = :comment_id
        '''), {"comment_id": comment_id}).fetchone()
        
        title = "Unknown Post"
        if comment_info:
            try:
                # Try different ways to access title
                if hasattr(comment_info, "_mapping"):
                    title = comment_info._mapping["title"]
                else:
                    # Second column should be title
                    title = comment_info[1]
            except Exception as e:
                print(f"Error getting post title: {e}")
            
            # Create notification
            Notification.create_comment_like_notification(username, False, title)
        
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
    comment = conn.execute(text('SELECT liked_by_author FROM comments WHERE id = :comment_id'), 
                          {"comment_id": comment_id}).fetchone()
    
    if not comment:
        return jsonify({'success': False, 'error': 'Comment not found'}), 404
    
    # Get liked_by_author value, handling different row types
    liked_by_author = 0
    try:
        if hasattr(comment, "_mapping"):
            liked_by_author = comment._mapping["liked_by_author"]
        else:
            # First column is liked_by_author
            liked_by_author = comment[0]
    except Exception as e:
        print(f"Error getting liked_by_author: {e}")
    
    # Toggle the status
    new_status = not bool(liked_by_author)
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
    # Try to initialize the database if needed
    if not ensure_db_initialized():
        return render_template('error.html', 
                              error_message="Database is currently unavailable. Please try again later.",
                              error_title="Database Error")

    try:
        analytics = Post.get_analytics()
        
        # If analytics returned None (e.g., due to error), provide default empty structure
        if analytics is None:
            analytics = []
        
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
    except Exception as e:
        print(f"Error in blog analytics: {e}")
        return render_template('error.html',
                              error_message="Error loading blog analytics. Please try again later.",
                              error_title="Analytics Error")

@app.route('/analytics/cv-analytics')
def cv_analytics():
    """CV download analytics"""
    # Try to initialize the database if needed
    if not ensure_db_initialized():
        return render_template('error.html', 
                              error_message="Database is currently unavailable. Please try again later.",
                              error_title="Database Error")
                              
    try:
        analytics = CVDownload.get_analytics()
        
        # If analytics returned None (e.g., due to error), provide default empty structure
        if analytics is None:
            analytics = {
                'total': 0,
                'by_reason': [],
                'registered': 0,
                'anonymous': 0,
                'recent': []
            }
        
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
    except Exception as e:
        print(f"Error in CV analytics: {e}")
        return render_template('error.html',
                              error_message="Error loading CV analytics. Please try again later.",
                              error_title="Analytics Error")

@app.route('/analytics/visitor-analytics')
def visitor_analytics():
    """Visitor statistics"""
    # Try to initialize the database if needed
    if not ensure_db_initialized():
        return render_template('error.html', 
                              error_message="Database is currently unavailable. Please try again later.",
                              error_title="Database Error")
                              
    try:
        analytics = VisitorStat.get_analytics()
        
        # If there was an error and analytics is None, provide a default empty structure
        if analytics is None:
            analytics = {
                'total_views': 0,
                'unique_visitors': 0,
                'popular_pages': [],
                'views_by_day': []
            }
        
        # Filter sensitive information for non-admin users
        if not session.get('user_id') or session.get('role') != 'admin':
            # Remove IP addresses or other sensitive data
            pass  # Specific filtering based on what's in the analytics
        
        return render_template('analytics/visitor_analytics.html', analytics=analytics)
    except Exception as e:
        print(f"Error in visitor analytics: {e}")
        return render_template('error.html',
                              error_message="Error loading visitor analytics. Please try again later.",
                              error_title="Analytics Error")

@app.route('/analytics/user-analytics')
@login_required
@admin_required
def user_analytics():
    """User statistics"""
    # Try to initialize the database if needed
    if not ensure_db_initialized():
        return render_template('error.html', 
                              error_message="Database is currently unavailable. Please try again later.",
                              error_title="Database Error")
                              
    try:
        # Get fresh data directly from the database to ensure accuracy
        conn = get_db_connection()
        
        # Check if we're using PostgreSQL or SQLite
        is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
        
        # Get total users count
        result = conn.execute(text('SELECT COUNT(*) as count FROM users')).fetchone()
        # Access count safely
        total_users = 0
        try:
            if hasattr(result, "_mapping"):
                total_users = result._mapping["count"]
            else:
                # Try accessing by position - count is the first column
                total_users = result[0]
        except Exception as e:
            print(f"Error accessing count: {e}")
        
        # Get users by role
        by_role_query = text('''
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role 
            ORDER BY count DESC
        ''')
        by_role_rows = conn.execute(by_role_query).fetchall()
        by_role = []
        for row in by_role_rows:
            try:
                if hasattr(row, "_mapping"):
                    by_role.append(dict(row._mapping))
                else:
                    # Assume first column is role, second is count
                    by_role.append({"role": row[0], "count": row[1]})
            except Exception as e:
                print(f"Error processing row: {e}")
        
        # Check which columns exist in the users table
        columns = []
        if is_postgres:
            # PostgreSQL query to get column names
            table_info_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
            """)
            table_info_rows = conn.execute(table_info_query).fetchall()
            
            for row in table_info_rows:
                try:
                    if hasattr(row, "_mapping"):
                        columns.append(row._mapping["column_name"])
                    else:
                        # column_name is the first column
                        columns.append(row[0])
                except Exception as e:
                    print(f"Error getting column name: {e}")
        else:
            # SQLite PRAGMA query
            table_info_rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
            
            for row in table_info_rows:
                try:
                    if hasattr(row, "_mapping"):
                        columns.append(row._mapping["name"])
                    else:
                        # "name" is typically the 2nd column in PRAGMA table_info result
                        columns.append(row[1])
                except Exception as e:
                    print(f"Error getting column name: {e}")
        
        # Get all users for the table view with most recent first
        # Determine if created_at exists, otherwise use registration_date or id as fallback
        if 'created_at' in columns:
            order_by = 'created_at DESC'
            all_users_query = text(f'''
                SELECT id, username, email, role, created_at 
                FROM users 
                ORDER BY {order_by}
            ''')
        else:
            # Fallback to ordering by ID if created_at doesn't exist
            order_by = 'id DESC'
            all_users_query = text(f'''
                SELECT id, username, email, role
                FROM users 
                ORDER BY {order_by}
            ''')
        
        all_users_rows = conn.execute(all_users_query).fetchall()
        all_users_list = []
        
        for row in all_users_rows:
            try:
                if hasattr(row, "_mapping"):
                    all_users_list.append(dict(row._mapping))
                else:
                    # Create dict from tuple assuming column order from query
                    user_dict = {}
                    if 'created_at' in columns:
                        user_dict = {"id": row[0], "username": row[1], "email": row[2], "role": row[3], "created_at": row[4]}
                    else:
                        user_dict = {"id": row[0], "username": row[1], "email": row[2], "role": row[3]}
                    all_users_list.append(user_dict)
            except Exception as e:
                print(f"Error processing user row: {e}")
        
        # If created_at doesn't exist in the result, add a placeholder
        if all_users_list and 'created_at' not in all_users_list[0]:
            for user in all_users_list:
                user['created_at'] = 'Not recorded'
        
        # Build the analytics dictionary
        analytics = {
            'total_users': total_users,
            'by_role': by_role,
            'all_users': all_users_list
        }
        
        return render_template('analytics/user_analytics.html', analytics=analytics)
    except Exception as e:
        print(f"Error in user analytics: {e}")
        return render_template('error.html',
                              error_message="Error loading user analytics. Please try again later.",
                              error_title="Analytics Error")

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

@app.route('/send-verification-link', methods=['POST'])
def send_verification_link():
    """Send a verification link for CV download"""
    # Get data from request
    if request.is_json:
        data = request.get_json()
        email = data.get('email')
        reason = data.get('reason')
    else:
        email = request.form.get('email')
        reason = request.form.get('reason')
    
    # Validate input
    if not email or not reason:
        return jsonify({
            'success': False,
            'message': 'Email and reason are required'
        }), 400
    
    # Generate token with email and reason
    token_data = {'email': email, 'reason': reason}
    token = serializer.dumps(token_data)
    
    # Calculate expiration (5 minutes from now)
    expires_at = datetime.now() + timedelta(minutes=5)
    
    # Store token in database
    verification_id = CVVerification.create(email, reason, token, expires_at.strftime('%Y-%m-%d %H:%M:%S'))
    
    if not verification_id:
        return jsonify({
            'success': False,
            'message': 'Failed to create verification record'
        }), 500
    
    # Create verification link
    verification_link = url_for('verify_download', token=token, _external=True)
    
    # Fallback for environments where _external=True doesn't generate absolute URLs
    if not verification_link.startswith(('http://', 'https://')):
        base_url = get_app_base_url()
        relative_path = url_for('verify_download', token=token).lstrip('/')
        verification_link = f"{base_url}/{relative_path}"
    
    # Create email message
    msg = Message(
        subject="Verify Your CV Download - Mohamad Arouni",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email],
        html=render_template(
            'email/verify_download.html', 
            verification_link=verification_link,
            reason=reason,
            expires_in="5 minutes"
        )
    )
    
    try:
        # Send email
        mail.send(msg)
        
        return jsonify({
            'success': True,
            'message': 'Verification link sent. Please check your email to continue.'
        })
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({
            'success': False,
            'message': 'Unable to send verification email. Please check your email address or try again later.'
        }), 500

@app.route('/verify-download')
def verify_download():
    """Handle verification link and trigger download"""
    token = request.args.get('token')
    
    if not token:
        return redirect(url_for('home', error='Invalid verification link'))
    
    try:
        # Validate token (5 minute expiration)
        token_data = serializer.loads(token, max_age=300)  # 300 seconds = 5 minutes
        email = token_data.get('email')
        reason = token_data.get('reason')
        
        # Get verification from database
        verification = CVVerification.get_by_token(token)
        
        if not verification:
            return redirect(url_for('home', error='Invalid verification link'))
            
        # Check if token is already used
        if verification.get('is_used'):
            return redirect(url_for('home', error='This verification link has already been used'))
            
        # Mark token as used
        CVVerification.mark_as_used(token)
        
        # Record the verified download
        CVDownload.create(reason, None, request.remote_addr, email=email, is_verified=True)
        
        # Create notification
        Notification.create_cv_download_notification('Verified User', True, reason)
        
        # Redirect to home with download parameter
        return redirect(url_for('home', download='cv'))
        
    except SignatureExpired:
        return redirect(url_for('home', error='Verification link has expired. Please request a new one.'))
    except BadSignature:
        return redirect(url_for('home', error='Invalid verification link'))
    except Exception as e:
        print(f"Error verifying download: {e}")
        return redirect(url_for('home', error='An error occurred while processing your request'))

# Helper function to get application URL
def get_app_base_url():
    """Get the base URL for the application based on the environment"""
    # Check for Railway environment variables
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    if railway_env:
        # If on Railway, use the provided domain
        return f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'your-domain.up.railway.app')}"
    
    # Fallback to request.host_url for local development
    if request and hasattr(request, 'host_url'):
        return request.host_url.rstrip('/')
    
    # Final fallback - shouldn't reach here if configured correctly
    return "http://localhost:5000"

if __name__ == '__main__':
    app.run(debug=True) 