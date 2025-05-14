from db_init import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='subscriber')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    content = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    author_name = db.Column(db.String(80))
    liked_by_author = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogLike(db.Model):
    __tablename__ = 'blog_likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    username = db.Column(db.String(80))
    is_anonymous = db.Column(db.Boolean, default=True)
    anonymous_id = db.Column(db.String(80))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CommentLike(db.Model):
    __tablename__ = 'comment_likes'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CVDownload(db.Model):
    __tablename__ = 'cv_downloads'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    reason = db.Column(db.String(255))
    is_anonymous = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(45))
    email = db.Column(db.String(120))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VisitorStat(db.Model):
    __tablename__ = 'visitor_stats'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45))
    country = db.Column(db.String(80))
    page_visited = db.Column(db.String(255))
    is_unique = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    message = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    username = db.Column(db.String(80))
    is_anonymous = db.Column(db.Boolean, default=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CVVerification(db.Model):
    __tablename__ = 'cv_verifications'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    reason = db.Column(db.String(255))
    token = db.Column(db.String(255))
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 