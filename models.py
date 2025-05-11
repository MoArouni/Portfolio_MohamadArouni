from db_init import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask import g, request

class User:
    """User model for managing user operations"""
    
    @staticmethod
    def create(username, email, password, role='subscriber'):
        """Create a new user in the database"""
        conn = get_db_connection()
        try:
            # Check if this is the first user and make them an admin if so
            user_count = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
            if user_count == 0:
                role = 'admin'
                
            hashed_password = generate_password_hash(password)
            cursor = conn.execute(
                'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                (username, email, hashed_password, role)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except conn.IntegrityError:
            # Username or email already exists
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def exists_with_username(username):
        """Check if a user with the given username exists"""
        conn = get_db_connection()
        result = conn.execute('SELECT COUNT(*) as count FROM users WHERE username = ?', (username,)).fetchone()
        exists = result['count'] > 0 if result else False
        conn.close()
        return exists
        
    @staticmethod
    def exists_with_email(email):
        """Check if a user with the given email exists"""
        conn = get_db_connection()
        result = conn.execute('SELECT COUNT(*) as count FROM users WHERE email = ?', (email,)).fetchone()
        exists = result['count'] > 0 if result else False
        conn.close()
        return exists
    
    @staticmethod
    def authenticate(email, password):
        """Authenticate user with email and password"""
        user = User.get_by_email(email)
        if user and check_password_hash(user['password'], password):
            return user
        return None
        
    @staticmethod
    def get_analytics():
        """Get analytics data for users"""
        conn = None
        try:
            conn = get_db_connection()
            
            # Total users
            result = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
            total_users = result['count'] if result else 0
            
            # Users by role
            by_role_query = '''
                SELECT role, COUNT(*) as count 
                FROM users 
                GROUP BY role 
                ORDER BY count DESC
            '''
            by_role = conn.execute(by_role_query).fetchall()
            
            # Recent users
            recent_users_query = '''
                SELECT id, username, email, role, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 10
            '''
            recent_users = conn.execute(recent_users_query).fetchall()
            
            # All users for the table view
            all_users_query = '''
                SELECT id, username, email, role, created_at 
                FROM users 
                ORDER BY created_at DESC
            '''
            all_users = conn.execute(all_users_query).fetchall()
            
            # Build and return the analytics dictionary
            return {
                'total_users': total_users,
                'by_role': [dict(r) for r in by_role] if by_role else [],
                'recent_users': [dict(u) for u in recent_users] if recent_users else [],
                'all_users': [dict(u) for u in all_users] if all_users else []
            }
        except Exception as e:
            print(f"Error getting user analytics: {e}")
            # Return empty data structure instead of None
            return {
                'total_users': 0,
                'by_role': [],
                'recent_users': [],
                'all_users': []
            }
        finally:
            if conn:
                conn.close()

class Post:
    """Post model for blog post operations"""
    
    @staticmethod
    def _convert_post_timestamps(post_dict):
        """Convert string timestamps to datetime objects in a post dict"""
        if post_dict and 'created_at' in post_dict:
            try:
                post_dict['created_at'] = datetime.strptime(post_dict['created_at'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                # If conversion fails, keep the original value
                pass
        return post_dict
    
    @staticmethod
    def create(title, content, user_id=None):
        """Create a new blog post"""
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)',
            (title, content, user_id)
        )
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return post_id
    
    @staticmethod
    def get_all(month_filter=None):
        """Get all posts, with optional month filtering"""
        conn = get_db_connection()
        query = 'SELECT * FROM posts'
        params = []
        
        if month_filter:
            query += ' WHERE strftime("%Y-%m", created_at) = ?'
            params.append(month_filter)
        
        query += ' ORDER BY created_at DESC'
        posts = conn.execute(query, params).fetchall()
        conn.close()
        
        # Convert to list of dicts and convert timestamps
        return [Post._convert_post_timestamps(dict(post)) for post in posts]
    
    @staticmethod
    def get_latest(limit=2):
        """Get the latest n blog posts"""
        conn = get_db_connection()
        query = 'SELECT * FROM posts ORDER BY created_at DESC LIMIT ?'
        posts = conn.execute(query, (limit,)).fetchall()
        conn.close()
        
        # Convert to list of dicts and convert timestamps
        return [Post._convert_post_timestamps(dict(post)) for post in posts]
    
    @staticmethod
    def get_by_id(post_id):
        """Get post by ID"""
        conn = get_db_connection()
        post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
        conn.close()
        return Post._convert_post_timestamps(dict(post)) if post else None
    
    @staticmethod
    def delete(post_id):
        """Delete a post by ID"""
        conn = get_db_connection()
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_available_months():
        """Get list of months that have posts"""
        conn = get_db_connection()
        months = conn.execute('''
            SELECT DISTINCT 
                strftime('%Y-%m', created_at) as month_year,
                case 
                    when strftime('%m', created_at) = '01' then 'January ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '02' then 'February ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '03' then 'March ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '04' then 'April ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '05' then 'May ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '06' then 'June ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '07' then 'July ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '08' then 'August ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '09' then 'September ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '10' then 'October ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '11' then 'November ' || strftime('%Y', created_at)
                    when strftime('%m', created_at) = '12' then 'December ' || strftime('%Y', created_at)
                    else 'Unknown'
                end as month_name
            FROM posts
            WHERE created_at IS NOT NULL
            ORDER BY month_year DESC
        ''').fetchall()
        conn.close()
        return [dict(month) for month in months]

    @staticmethod
    def update(post_id, title, content):
        """Update an existing post"""
        conn = get_db_connection()
        try:
            conn.execute(
                'UPDATE posts SET title = ?, content = ? WHERE id = ?',
                (title, content, post_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating post: {e}")
            return False
        finally:
            conn.close()
            
    @staticmethod
    def increment_view_count(post_id):
        """Increment the view count for a post"""
        conn = get_db_connection()
        try:
            conn.execute(
                'UPDATE posts SET view_count = view_count + 1 WHERE id = ?',
                (post_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error incrementing view count: {e}")
            return False
        finally:
            conn.close()
            
    @staticmethod
    def get_analytics():
        """Get analytics for all blog posts"""
        conn = get_db_connection()
        posts_analytics = conn.execute('''
            SELECT 
                p.id,
                p.title,
                p.view_count,
                (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count,
                (SELECT COUNT(*) FROM blog_likes WHERE post_id = p.id) AS total_likes,
                (SELECT COUNT(*) FROM blog_likes WHERE post_id = p.id AND is_anonymous = 1) AS anonymous_likes,
                (SELECT COUNT(*) FROM blog_likes WHERE post_id = p.id AND is_anonymous = 0) AS registered_likes,
                (SELECT MAX(created_at) FROM blog_likes WHERE post_id = p.id) AS last_like_date,
                (SELECT MAX(created_at) FROM comments WHERE post_id = p.id) AS last_comment_date,
                p.created_at
            FROM posts p
            ORDER BY p.created_at DESC
        ''').fetchall()
        conn.close()
        
        # Convert to list of dicts
        return [dict(post) for post in posts_analytics]

class Comment:
    """Comment model for post comment operations"""
    
    @staticmethod
    def _convert_comment_timestamps(comment_dict):
        """Convert string timestamps to datetime objects in a comment dict"""
        if comment_dict and 'created_at' in comment_dict:
            try:
                comment_dict['created_at'] = datetime.strptime(comment_dict['created_at'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                # If conversion fails, keep the original value
                pass
        return comment_dict
    
    @staticmethod
    def create(post_id, content, user_id=None):
        """Create a new comment"""
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO comments (post_id, user_id, content, is_anonymous) VALUES (?, ?, ?, ?)',
            (post_id, user_id, content, 0)
        )
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return comment_id
    
    @staticmethod
    def create_anonymous(post_id, content, author_name):
        """Create a new anonymous comment"""
        conn = get_db_connection()
        cursor = conn.execute(
            'INSERT INTO comments (post_id, author_name, content, is_anonymous) VALUES (?, ?, ?, ?)',
            (post_id, author_name, content, 1)
        )
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return comment_id
    
    @staticmethod
    def get_for_post(post_id):
        """Get all comments for a post"""
        conn = get_db_connection()
        comments = conn.execute('''
            SELECT c.*, u.username,
                   (SELECT COUNT(*) FROM comment_likes WHERE comment_id = c.id) AS like_count,
                   c.liked_by_author,
                   c.is_anonymous,
                   c.author_name
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.created_at DESC
        ''', (post_id,)).fetchall()
        conn.close()
        return [Comment._convert_comment_timestamps(dict(comment)) for comment in comments]
    
    @staticmethod
    def delete(comment_id):
        """Delete a comment by ID"""
        conn = get_db_connection()
        conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.commit()
        conn.close()
        return True
        
    @staticmethod
    def toggle_author_like(comment_id, liked=True):
        """Toggle the liked_by_author flag for a comment"""
        conn = get_db_connection()
        try:
            conn.execute(
                'UPDATE comments SET liked_by_author = ? WHERE id = ?',
                (1 if liked else 0, comment_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error toggling author like: {e}")
            return False
        finally:
            conn.close()

class BlogLike:
    """Blog like model for managing blog post likes"""
    
    @staticmethod
    def create(post_id, user_id=None, username=None, is_anonymous=True):
        """Create a new blog like"""
        conn = get_db_connection()
        
        # Check if like already exists for this user/post combination
        if user_id:
            existing = conn.execute(
                'SELECT id FROM blog_likes WHERE post_id = ? AND user_id = ?',
                (post_id, user_id)
            ).fetchone()
            
            if existing:
                conn.close()
                return None  # User already liked this post
        
        try:
            cursor = conn.execute(
                'INSERT INTO blog_likes (post_id, user_id, username, is_anonymous) VALUES (?, ?, ?, ?)',
                (post_id, user_id, username, 1 if is_anonymous else 0)
            )
            like_id = cursor.lastrowid
            conn.commit()
            return like_id
        except Exception as e:
            print(f"Error creating blog like: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def delete(like_id=None, post_id=None, user_id=None):
        """Delete a blog like by ID or post/user combo"""
        conn = get_db_connection()
        try:
            if like_id:
                conn.execute('DELETE FROM blog_likes WHERE id = ?', (like_id,))
            elif post_id and user_id:
                conn.execute('DELETE FROM blog_likes WHERE post_id = ? AND user_id = ?', 
                             (post_id, user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting blog like: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def has_user_liked(post_id, user_id):
        """Check if a user has liked a post"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT id FROM blog_likes WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        ).fetchone()
        conn.close()
        return bool(result)
    
    @staticmethod
    def get_count_for_post(post_id):
        """Get the count of likes for a post"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT COUNT(*) as count FROM blog_likes WHERE post_id = ?',
            (post_id,)
        ).fetchone()
        conn.close()
        return result['count'] if result else 0
    
    @staticmethod
    def get_total_likes_count():
        """Get the total count of all likes in the database"""
        try:
            conn = get_db_connection()
            result = conn.execute('SELECT COUNT(*) as count FROM blog_likes').fetchone()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting total likes count: {e}")
            return 0

    @staticmethod
    def create_anonymous(post_id, username='Anonymous', anonymous_id='', ip_address=None):
        """Create a new anonymous blog like with tracking"""
        conn = get_db_connection()
        
        # Check if like already exists for this anonymous user
        if anonymous_id:
            existing = conn.execute(
                'SELECT id FROM blog_likes WHERE post_id = ? AND anonymous_id = ?',
                (post_id, anonymous_id)
            ).fetchone()
            
            if existing:
                conn.close()
                return None  # Already liked from this anonymous ID
        
        # Check if like already exists for this IP (additional check)
        if ip_address:
            existing_ip = conn.execute(
                'SELECT id FROM blog_likes WHERE post_id = ? AND ip_address = ? AND is_anonymous = 1',
                (post_id, ip_address)
            ).fetchone()
            
            if existing_ip:
                conn.close()
                return None  # Already liked from this IP
        
        try:
            cursor = conn.execute(
                'INSERT INTO blog_likes (post_id, user_id, username, is_anonymous, anonymous_id, ip_address) VALUES (?, ?, ?, ?, ?, ?)',
                (post_id, None, username, 1, anonymous_id, ip_address)
            )
            like_id = cursor.lastrowid
            conn.commit()
            return like_id
        except Exception as e:
            print(f"Error creating anonymous blog like: {e}")
            return None
        finally:
            conn.close()

class CommentLike:
    """Comment like model for managing comment likes"""
    
    @staticmethod
    def create(comment_id, user_id):
        """Create a new comment like"""
        conn = get_db_connection()
        
        # Check if like already exists for this user/comment combination
        existing = conn.execute(
            'SELECT id FROM comment_likes WHERE comment_id = ? AND user_id = ?',
            (comment_id, user_id)
        ).fetchone()
        
        if existing:
            conn.close()
            return None  # User already liked this comment
        
        try:
            cursor = conn.execute(
                'INSERT INTO comment_likes (comment_id, user_id) VALUES (?, ?)',
                (comment_id, user_id)
            )
            like_id = cursor.lastrowid
            conn.commit()
            return like_id
        except Exception as e:
            print(f"Error creating comment like: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def delete(comment_id, user_id):
        """Delete a comment like by comment_id and user_id"""
        conn = get_db_connection()
        try:
            conn.execute(
                'DELETE FROM comment_likes WHERE comment_id = ? AND user_id = ?',
                (comment_id, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting comment like: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def has_user_liked(comment_id, user_id):
        """Check if a user has liked a comment"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT id FROM comment_likes WHERE comment_id = ? AND user_id = ?',
            (comment_id, user_id)
        ).fetchone()
        conn.close()
        return bool(result)
    
    @staticmethod
    def get_count_for_comment(comment_id):
        """Get the count of likes for a comment"""
        conn = get_db_connection()
        result = conn.execute(
            'SELECT COUNT(*) as count FROM comment_likes WHERE comment_id = ?',
            (comment_id,)
        ).fetchone()
        conn.close()
        return result['count'] if result else 0

class CVDownload:
    """CV Download model for tracking CV downloads"""
    
    @staticmethod
    def create(reason, user_id=None, ip_address=None):
        """Record a CV download"""
        conn = get_db_connection()
        try:
            is_anonymous = user_id is None
            cursor = conn.execute(
                'INSERT INTO cv_downloads (user_id, reason, is_anonymous, ip_address) VALUES (?, ?, ?, ?)',
                (user_id, reason, 1 if is_anonymous else 0, ip_address)
            )
            download_id = cursor.lastrowid
            conn.commit()
            return download_id
        except Exception as e:
            print(f"Error recording CV download: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_analytics():
        """Get analytics for CV downloads"""
        conn = get_db_connection()
        try:
            # Total downloads
            total = conn.execute('SELECT COUNT(*) as count FROM cv_downloads').fetchone()['count']
            
            # Downloads by reason
            by_reason = conn.execute('''
                SELECT reason, COUNT(*) as count 
                FROM cv_downloads 
                GROUP BY reason 
                ORDER BY count DESC
            ''').fetchall()
            
            # Registered vs anonymous
            by_type = conn.execute('''
                SELECT 
                    SUM(CASE WHEN is_anonymous = 0 THEN 1 ELSE 0 END) as registered,
                    SUM(CASE WHEN is_anonymous = 1 THEN 1 ELSE 0 END) as anonymous
                FROM cv_downloads
            ''').fetchone()
            
            # Recent downloads
            recent = conn.execute('''
                SELECT 
                    cv.id,
                    cv.reason,
                    cv.is_anonymous,
                    u.username,
                    cv.created_at
                FROM cv_downloads cv
                LEFT JOIN users u ON cv.user_id = u.id
                ORDER BY cv.created_at DESC
                LIMIT 10
            ''').fetchall()
            
            conn.close()
            
            return {
                'total': total,
                'by_reason': [dict(r) for r in by_reason],
                'registered': by_type['registered'],
                'anonymous': by_type['anonymous'],
                'recent': [dict(r) for r in recent]
            }
        except Exception as e:
            print(f"Error getting CV download analytics: {e}")
            conn.close()
            return None

class VisitorStat:
    """Visitor statistics model for tracking page views"""
    
    @staticmethod
    def record_visit(ip_address, page_visited, country=None):
        """Record a page visit"""
        conn = get_db_connection()
        try:
            # Check if this IP has visited before
            is_unique = 1
            existing = conn.execute(
                'SELECT id FROM visitor_stats WHERE ip_address = ?',
                (ip_address,)
            ).fetchone()
            
            if existing:
                is_unique = 0
            
            cursor = conn.execute(
                'INSERT INTO visitor_stats (ip_address, country, page_visited, is_unique) VALUES (?, ?, ?, ?)',
                (ip_address, country, page_visited, is_unique)
            )
            visitor_id = cursor.lastrowid
            conn.commit()
            return visitor_id
        except Exception as e:
            print(f"Error recording visitor stat: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_analytics():
        """Get visitor analytics"""
        conn = get_db_connection()
        try:
            # Total page views
            total_views = conn.execute('SELECT COUNT(*) as count FROM visitor_stats').fetchone()['count']
            
            # Unique visitors
            unique_visitors = conn.execute(
                'SELECT COUNT(DISTINCT ip_address) as count FROM visitor_stats'
            ).fetchone()['count']
            
            # Most visited pages
            popular_pages = conn.execute('''
                SELECT 
                    page_visited, 
                    COUNT(*) as count
                FROM visitor_stats
                GROUP BY page_visited
                ORDER BY count DESC
                LIMIT 10
            ''').fetchall()
            
            # Views over time (last 7 days)
            views_by_day = conn.execute('''
                SELECT 
                    date(created_at) as date,
                    COUNT(*) as count
                FROM visitor_stats
                WHERE created_at >= date('now', '-7 days')
                GROUP BY date
                ORDER BY date
            ''').fetchall()
            
            conn.close()
            
            return {
                'total_views': total_views,
                'unique_visitors': unique_visitors,
                'popular_pages': [dict(p) for p in popular_pages],
                'views_by_day': [dict(d) for d in views_by_day]
            }
        except Exception as e:
            print(f"Error getting visitor analytics: {e}")
            conn.close()
            return None

class Notification:
    """Notification model for admin dashboard notifications"""
    
    # Notification types
    TYPE_COMMENT = 'comment'
    TYPE_LIKE_POST = 'like_post'
    TYPE_LIKE_COMMENT = 'like_comment'
    TYPE_CV_DOWNLOAD = 'cv_download'
    TYPE_VIEW_MILESTONE = 'view_milestone'
    TYPE_NEW_USER = 'new_user'
    
    @staticmethod
    def create(type, message, user_id=None, username=None, is_anonymous=True):
        """Create a new notification"""
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                'INSERT INTO notifications (type, message, user_id, username, is_anonymous, is_read) VALUES (?, ?, ?, ?, ?, ?)',
                (type, message, user_id, username, 1 if is_anonymous else 0, 0)
            )
            notification_id = cursor.lastrowid
            conn.commit()
            return notification_id
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark a notification as read"""
        conn = get_db_connection()
        try:
            conn.execute(
                'UPDATE notifications SET is_read = 1 WHERE id = ?',
                (notification_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_recent(limit=10):
        """Get recent notifications"""
        conn = get_db_connection()
        try:
            notifications = conn.execute('''
                SELECT 
                    id,
                    type,
                    message,
                    username,
                    is_anonymous,
                    is_read,
                    created_at
                FROM notifications
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,)).fetchall()
            
            conn.close()
            
            # Convert to list of dicts with relative time
            result = []
            for notification in notifications:
                notification_dict = dict(notification)
                
                # Calculate relative time
                created_at = datetime.strptime(notification_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                diff = now - created_at
                
                if diff.days > 0:
                    relative_time = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
                elif diff.seconds >= 3600:
                    hours = diff.seconds // 3600
                    relative_time = f"{hours} hour{'s' if hours > 1 else ''} ago"
                elif diff.seconds >= 60:
                    minutes = diff.seconds // 60
                    relative_time = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                else:
                    relative_time = "just now"
                
                notification_dict['relative_time'] = relative_time
                result.append(notification_dict)
            
            return result
        except Exception as e:
            print(f"Error getting recent notifications: {e}")
            conn.close()
            return []
            
    @staticmethod
    def create_comment_notification(username, is_anonymous, post_title):
        """Create a notification for a new comment"""
        user_display = 'Anonymous' if is_anonymous else username
        message = f"{user_display} posted a comment on '{post_title}'!"
        return Notification.create(Notification.TYPE_COMMENT, message, username=username, is_anonymous=is_anonymous)
    
    @staticmethod
    def create_post_like_notification(username, is_anonymous, post_title):
        """Create a notification for a post like"""
        user_display = 'Anonymous' if is_anonymous else username
        message = f"{user_display} liked your post '{post_title}'!"
        return Notification.create(Notification.TYPE_LIKE_POST, message, username=username, is_anonymous=is_anonymous)
    
    @staticmethod
    def create_comment_like_notification(username, is_anonymous, post_title):
        """Create a notification for a comment like"""
        user_display = 'Anonymous' if is_anonymous else username
        message = f"{user_display} liked a comment on '{post_title}'!"
        return Notification.create(Notification.TYPE_LIKE_COMMENT, message, username=username, is_anonymous=is_anonymous)
    
    @staticmethod
    def create_cv_download_notification(username, is_anonymous, reason):
        """Create a notification for a CV download"""
        user_display = 'Anonymous' if is_anonymous else username
        message = f"{user_display} downloaded your CV for {reason}!"
        return Notification.create(Notification.TYPE_CV_DOWNLOAD, message, username=username, is_anonymous=is_anonymous)
    
    @staticmethod
    def create_view_milestone_notification(count):
        """Create a notification for a view milestone"""
        message = f"Your website got viewed {count} times!"
        return Notification.create(Notification.TYPE_VIEW_MILESTONE, message)
    
    @staticmethod
    def create_new_user_notification(username):
        """Create a notification for a new registered user"""
        message = f"{username} is now a registered user!"
        return Notification.create(Notification.TYPE_NEW_USER, message, username=username, is_anonymous=False) 