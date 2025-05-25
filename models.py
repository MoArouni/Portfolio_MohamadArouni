from db_init import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask import g, request
from sqlalchemy.sql import text

class User:
    """User model for managing user operations"""
    
    @staticmethod
    def create(username, email, password, role='subscriber'):
        """Create a new user in the database"""
        conn = get_db_connection()
        try:
            # Check if this is the first user and make them an admin if so
            user_count_result = conn.execute(text('SELECT COUNT(*) as count FROM users')).fetchone()
            
            # Handle different result row types
            user_count = 0
            if user_count_result:
                try:
                    if hasattr(user_count_result, "_mapping"):
                        user_count = user_count_result._mapping["count"]
                    else:
                        # In tuple form, the count should be the first column
                        user_count = user_count_result[0]
                except Exception as e:
                    print(f"Error accessing user count: {e}")
            
            if user_count == 0:
                role = 'admin'
                
            hashed_password = generate_password_hash(password)
            cursor = conn.execute(
                text('INSERT INTO users (username, email, password, role) VALUES (:username, :email, :password, :role)'),
                {"username": username, "email": email, "password": hashed_password, "role": role}
            )
            # For SQLite compatibility
            if hasattr(cursor, 'lastrowid'):
                user_id = cursor.lastrowid
            else:
                # For PostgreSQL, use RETURNING id which we already set up in the db_init.py
                user_id = cursor.fetchone()[0] if cursor.returns_rows else None
                
            conn.commit()
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        user = conn.execute(text('SELECT * FROM users WHERE id = :user_id'), {"user_id": user_id}).fetchone()
        if not user:
            return None
            
        # Handle different types of result rows
        try:
            if hasattr(user, "_mapping"):
                return dict(user._mapping)
            else:
                # Create a dict manually from the row tuple
                # Assuming columns are: id, username, email, password, role, created_at
                columns = ["id", "username", "email", "password", "role", "created_at"]
                return {columns[i]: user[i] for i in range(min(len(columns), len(user)))}
        except Exception as e:
            print(f"Error converting user row to dict: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        conn = get_db_connection()
        user = conn.execute(text('SELECT * FROM users WHERE email = :email'), {"email": email}).fetchone()
        if not user:
            return None
            
        # Handle different types of result rows
        try:
            if hasattr(user, "_mapping"):
                return dict(user._mapping)
            else:
                # Create a dict manually from the row tuple
                # Assuming columns are: id, username, email, password, role, created_at
                columns = ["id", "username", "email", "password", "role", "created_at"]
                return {columns[i]: user[i] for i in range(min(len(columns), len(user)))}
        except Exception as e:
            print(f"Error converting user row to dict: {e}")
            return None
    
    @staticmethod
    def exists_with_username(username):
        """Check if a user with the given username exists"""
        conn = get_db_connection()
        result = conn.execute(text('SELECT COUNT(*) as count FROM users WHERE username = :username'), {"username": username}).fetchone()
        
        # Handle different result row types (dict-like or tuple)
        if result:
            try:
                if hasattr(result, "_mapping"):
                    return result._mapping["count"] > 0
                else:
                    # In tuple form, the count should be the first column
                    return result[0] > 0
            except Exception as e:
                print(f"Error accessing count: {e}")
                return False
        return False
        
    @staticmethod
    def exists_with_email(email):
        """Check if a user with the given email exists"""
        conn = get_db_connection()
        result = conn.execute(text('SELECT COUNT(*) as count FROM users WHERE email = :email'), {"email": email}).fetchone()
        
        # Handle different result row types (dict-like or tuple)
        if result:
            try:
                if hasattr(result, "_mapping"):
                    return result._mapping["count"] > 0
                else:
                    # In tuple form, the count should be the first column
                    return result[0] > 0
            except Exception as e:
                print(f"Error accessing count: {e}")
                return False
        return False
    
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
            result = conn.execute(text('SELECT COUNT(*) as count FROM users')).fetchone()
            total_users = result['count'] if result else 0
            
            # Users by role
            by_role_query = text('''
                SELECT role, COUNT(*) as count 
                FROM users 
                GROUP BY role 
                ORDER BY count DESC
            ''')
            by_role = conn.execute(by_role_query).fetchall()
            
            # Recent users
            recent_users_query = text('''
                SELECT id, username, email, role, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 10
            ''')
            recent_users = conn.execute(recent_users_query).fetchall()
            
            # All users for the table view
            all_users_query = text('''
                SELECT id, username, email, role, created_at 
                FROM users 
                ORDER BY created_at DESC
            ''')
            all_users = conn.execute(all_users_query).fetchall()
            
            # Build and return the analytics dictionary
            return {
                'total_users': total_users,
                'by_role': [dict(r._mapping) for r in by_role] if by_role else [],
                'recent_users': [dict(u._mapping) for u in recent_users] if recent_users else [],
                'all_users': [dict(u._mapping) for u in all_users] if all_users else []
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
            text('INSERT INTO posts (title, content, user_id) VALUES (:title, :content, :user_id)'),
            {"title": title, "content": content, "user_id": user_id}
        )
        # For SQLite compatibility
        if hasattr(cursor, 'lastrowid'):
            post_id = cursor.lastrowid
        else:
            # For PostgreSQL
            post_id = cursor.fetchone()[0] if cursor.returns_rows else None
            
        conn.commit()
        return post_id
    
    @staticmethod
    def get_all(month_filter=None):
        """Get all posts, with optional month filtering"""
        conn = get_db_connection()
        try:
            # Check if we're using PostgreSQL or SQLite
            from app import app
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            if month_filter:
                if is_postgres:
                    # PostgreSQL uses to_char
                    query = text('''
                        SELECT * FROM posts 
                        WHERE to_char(created_at, 'YYYY-MM') = :month_filter
                        ORDER BY created_at DESC
                    ''')
                else:
                    # SQLite uses strftime
                    query = text('''
                        SELECT * FROM posts 
                        WHERE strftime('%Y-%m', created_at) = :month_filter
                        ORDER BY created_at DESC
                    ''')
                posts = conn.execute(query, {"month_filter": month_filter}).fetchall()
            else:
                query = text('SELECT * FROM posts ORDER BY created_at DESC')
                posts = conn.execute(query).fetchall()
            
            # Convert to list of dicts
            result = []
            for post in posts:
                try:
                    if hasattr(post, "_mapping"):
                        result.append(Post._convert_post_timestamps(dict(post._mapping)))
                    else:
                        # Create dict manually - assuming columns: id, title, content, user_id, view_count, created_at
                        columns = ["id", "title", "content", "user_id", "view_count", "created_at"]
                        post_dict = {columns[i]: post[i] for i in range(min(len(columns), len(post)))}
                        result.append(Post._convert_post_timestamps(post_dict))
                except Exception as e:
                    print(f"Error processing post: {e}")
                
            return result
        except Exception as e:
            print(f"Error getting posts: {e}")
            try:
                conn.rollback()
            except:
                pass
            return []  # Return empty list on error
    
    @staticmethod
    def get_latest(limit=2):
        """Get the latest n blog posts"""
        conn = get_db_connection()
        try:
            query = text('SELECT * FROM posts ORDER BY created_at DESC LIMIT :limit')
            posts = conn.execute(query, {"limit": limit}).fetchall()
            
            # Convert to list of dicts and convert timestamps
            return [Post._convert_post_timestamps(dict(post._mapping)) for post in posts]
        except Exception as e:
            print(f"Error getting latest posts: {e}")
            try:
                conn.rollback()
            except:
                pass
            return []  # Return empty list on error
    
    @staticmethod
    def get_by_id(post_id):
        """Get post by ID"""
        conn = get_db_connection()
        post = conn.execute(text('SELECT * FROM posts WHERE id = :post_id'), {"post_id": post_id}).fetchone()
        if not post:
            return None
            
        # Handle different types of result rows
        post_dict = None
        try:
            if hasattr(post, "_mapping"):
                post_dict = dict(post._mapping)
            else:
                # Create a dict manually from the row tuple
                # Assuming columns are: id, title, content, user_id, view_count, created_at
                columns = ["id", "title", "content", "user_id", "view_count", "created_at"]
                post_dict = {columns[i]: post[i] for i in range(min(len(columns), len(post)))}
        except Exception as e:
            print(f"Error converting post row to dict: {e}")
            return None
            
        return Post._convert_post_timestamps(post_dict)
    
    @staticmethod
    def delete(post_id):
        """Delete a post by ID"""
        conn = get_db_connection()
        conn.execute(text('DELETE FROM posts WHERE id = :post_id'), {"post_id": post_id})
        conn.commit()
        return True
    
    @staticmethod
    def get_available_months():
        """Get list of months that have posts"""
        conn = get_db_connection()
        
        try:
            # Check if we're using PostgreSQL or SQLite
            from app import app
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            if is_postgres:
                # PostgreSQL version using date_trunc and to_char
                query = text('''
                    SELECT DISTINCT 
                        to_char(created_at, 'YYYY-MM') as month_year,
                        CASE 
                            WHEN to_char(created_at, 'MM') = '01' THEN 'January ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '02' THEN 'February ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '03' THEN 'March ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '04' THEN 'April ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '05' THEN 'May ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '06' THEN 'June ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '07' THEN 'July ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '08' THEN 'August ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '09' THEN 'September ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '10' THEN 'October ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '11' THEN 'November ' || to_char(created_at, 'YYYY')
                            WHEN to_char(created_at, 'MM') = '12' THEN 'December ' || to_char(created_at, 'YYYY')
                            ELSE 'Unknown'
                        END as month_name
                    FROM posts
                    WHERE created_at IS NOT NULL
                    ORDER BY month_year DESC
                ''')
            else:
                # SQLite version using strftime
                query = text('''
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
                ''')
            
            months = conn.execute(query).fetchall()
            result = []
            
            # Handle different row types safely
            for month in months:
                try:
                    if hasattr(month, "_mapping"):
                        result.append(dict(month._mapping))
                    else:
                        # Create dict manually
                        result.append({"month_year": month[0], "month_name": month[1]})
                except Exception as e:
                    print(f"Error processing month: {e}")
                
            return result
        except Exception as e:
            print(f"Error getting available months: {e}")
            try:
                conn.rollback()
            except:
                pass
            return []  # Return empty list on error

    @staticmethod
    def update(post_id, title, content):
        """Update an existing post"""
        conn = get_db_connection()
        try:
            conn.execute(
                text('UPDATE posts SET title = :title, content = :content WHERE id = :post_id'),
                {"title": title, "content": content, "post_id": post_id}
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating post: {e}")
            return False
            
    @staticmethod
    def increment_view_count(post_id):
        """Increment the view count for a post"""
        conn = get_db_connection()
        try:
            conn.execute(
                text('UPDATE posts SET view_count = view_count + 1 WHERE id = :post_id'),
                {"post_id": post_id}
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error incrementing view count: {e}")
            return False
            
    @staticmethod
    def get_analytics():
        """Get analytics for all blog posts"""
        conn = get_db_connection()
        try:
            posts_analytics = conn.execute(text('''
                SELECT 
                    p.id,
                    p.title,
                    p.view_count,
                    (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count,
                    (SELECT COUNT(*) FROM blog_likes WHERE post_id = p.id) AS total_likes,
                    (SELECT COUNT(*) FROM blog_likes WHERE post_id = p.id AND is_anonymous = TRUE) AS anonymous_likes,
                    (SELECT COUNT(*) FROM blog_likes WHERE post_id = p.id AND is_anonymous = FALSE) AS registered_likes,
                    (SELECT MAX(created_at) FROM blog_likes WHERE post_id = p.id) AS last_like_date,
                    (SELECT MAX(created_at) FROM comments WHERE post_id = p.id) AS last_comment_date,
                    p.created_at
                FROM posts p
                ORDER BY p.created_at DESC
            ''')).fetchall()
            
            # Convert to list of dicts
            result = []
            for post in posts_analytics:
                try:
                    if hasattr(post, "_mapping"):
                        result.append(dict(post._mapping))
                    else:
                        # Create dict manually - mapping column names to values
                        column_names = ["id", "title", "view_count", "comment_count", "total_likes", 
                                      "anonymous_likes", "registered_likes", "last_like_date", 
                                      "last_comment_date", "created_at"]
                        post_dict = {column_names[i]: post[i] for i in range(min(len(column_names), len(post)))}
                        result.append(post_dict)
                except Exception as e:
                    print(f"Error processing post analytics: {e}")
                
            return result
        except Exception as e:
            print(f"Error getting post analytics: {e}")
            try:
                conn.rollback()
            except:
                pass
            return []  # Return empty list on error

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
            text('INSERT INTO comments (post_id, user_id, content, is_anonymous) VALUES (:post_id, :user_id, :content, :is_anonymous)'),
            {"post_id": post_id, "user_id": user_id, "content": content, "is_anonymous": False}
        )
        # For SQLite compatibility
        if hasattr(cursor, 'lastrowid'):
            comment_id = cursor.lastrowid
        else:
            # For PostgreSQL
            comment_id = cursor.fetchone()[0] if cursor.returns_rows else None
            
        conn.commit()
        return comment_id
    
    @staticmethod
    def create_anonymous(post_id, content, author_name):
        """Create a new anonymous comment"""
        conn = get_db_connection()
        cursor = conn.execute(
            text('INSERT INTO comments (post_id, author_name, content, is_anonymous) VALUES (:post_id, :author_name, :content, :is_anonymous)'),
            {"post_id": post_id, "author_name": author_name, "content": content, "is_anonymous": True}
        )
        # For SQLite compatibility
        if hasattr(cursor, 'lastrowid'):
            comment_id = cursor.lastrowid
        else:
            # For PostgreSQL
            comment_id = cursor.fetchone()[0] if cursor.returns_rows else None
            
        conn.commit()
        return comment_id
    
    @staticmethod
    def get_for_post(post_id):
        """Get all comments for a post"""
        conn = get_db_connection()
        comments = conn.execute(text('''
            SELECT c.*, u.username,
                   (SELECT COUNT(*) FROM comment_likes WHERE comment_id = c.id) AS like_count,
                   c.liked_by_author,
                   c.is_anonymous,
                   c.author_name
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.post_id = :post_id
            ORDER BY c.created_at DESC
        '''), {"post_id": post_id}).fetchall()
        return [Comment._convert_comment_timestamps(dict(comment._mapping)) for comment in comments]
    
    @staticmethod
    def delete(comment_id):
        """Delete a comment by ID"""
        conn = get_db_connection()
        conn.execute(text('DELETE FROM comments WHERE id = :comment_id'), {"comment_id": comment_id})
        conn.commit()
        return True
        
    @staticmethod
    def toggle_author_like(comment_id, liked=True):
        """Toggle the liked_by_author flag for a comment"""
        conn = get_db_connection()
        try:
            conn.execute(
                text('UPDATE comments SET liked_by_author = :liked WHERE id = :comment_id'),
                {"liked": liked, "comment_id": comment_id}
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error toggling author like: {e}")
            return False

class BlogLike:
    """Blog like model for managing blog post likes"""
    
    @staticmethod
    def create(post_id, user_id=None, username=None, is_anonymous=True):
        """Create a new blog like"""
        conn = get_db_connection()
        
        # Check if like already exists for this user/post combination
        if user_id:
            existing = conn.execute(
                text('SELECT id FROM blog_likes WHERE post_id = :post_id AND user_id = :user_id'),
                {"post_id": post_id, "user_id": user_id}
            ).fetchone()
            
            if existing:
                return None  # User already liked this post
        
        try:
            cursor = conn.execute(
                text('INSERT INTO blog_likes (post_id, user_id, username, is_anonymous) VALUES (:post_id, :user_id, :username, :is_anonymous)'),
                {"post_id": post_id, "user_id": user_id, "username": username, "is_anonymous": is_anonymous}
            )
            # For SQLite compatibility
            if hasattr(cursor, 'lastrowid'):
                like_id = cursor.lastrowid
            else:
                # For PostgreSQL
                like_id = cursor.fetchone()[0] if cursor.returns_rows else None
                
            conn.commit()
            return like_id
        except Exception as e:
            print(f"Error creating blog like: {e}")
            return None
    
    @staticmethod
    def delete(like_id=None, post_id=None, user_id=None):
        """Delete a blog like by ID or post/user combo"""
        conn = get_db_connection()
        try:
            if like_id:
                conn.execute(text('DELETE FROM blog_likes WHERE id = :like_id'), {"like_id": like_id})
            elif post_id and user_id:
                conn.execute(text('DELETE FROM blog_likes WHERE post_id = :post_id AND user_id = :user_id'), 
                           {"post_id": post_id, "user_id": user_id})
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting blog like: {e}")
            return False
    
    @staticmethod
    def has_user_liked(post_id, user_id):
        """Check if a user has liked a post"""
        if not post_id or not user_id:
            return False
        
        conn = get_db_connection()
        try:
            result = conn.execute(
                text('SELECT id FROM blog_likes WHERE post_id = :post_id AND user_id = :user_id'),
                {"post_id": post_id, "user_id": user_id}
            ).fetchone()
            return bool(result)
        except Exception as e:
            print(f"Error checking if user liked post: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False  # Default to not liked on error
    
    @staticmethod
    def get_count_for_post(post_id):
        """Get the count of likes for a post"""
        conn = get_db_connection()
        result = conn.execute(
            text('SELECT COUNT(*) as count FROM blog_likes WHERE post_id = :post_id'),
            {"post_id": post_id}
        ).fetchone()
        
        # Handle different result row types (dict-like or tuple)
        if result:
            try:
                if hasattr(result, "_mapping"):
                    return result._mapping["count"]
                else:
                    # In tuple form, the count should be the first column
                    return result[0]
            except Exception as e:
                print(f"Error accessing count: {e}")
                return 0
        return 0
    
    @staticmethod
    def get_total_likes_count():
        """Get the total count of all likes in the database"""
        try:
            conn = get_db_connection()
            result = conn.execute(text('SELECT COUNT(*) as count FROM blog_likes')).fetchone()
            
            # Handle different result row types (dict-like or tuple)
            if result:
                try:
                    if hasattr(result, "_mapping"):
                        return result._mapping["count"]
                    else:
                        # In tuple form, the count should be the first column
                        return result[0]
                except Exception as e:
                    print(f"Error accessing count: {e}")
                    return 0
            return 0
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
                text('SELECT id FROM blog_likes WHERE post_id = :post_id AND anonymous_id = :anonymous_id'),
                {"post_id": post_id, "anonymous_id": anonymous_id}
            ).fetchone()
            
            if existing:
                return None  # Already liked from this anonymous ID
        
        # Check if like already exists for this IP (additional check)
        if ip_address:
            existing_ip = conn.execute(
                text('SELECT id FROM blog_likes WHERE post_id = :post_id AND ip_address = :ip_address AND is_anonymous = :is_anonymous'),
                {"post_id": post_id, "ip_address": ip_address, "is_anonymous": True}
            ).fetchone()
            
            if existing_ip:
                return None  # Already liked from this IP
        
        try:
            cursor = conn.execute(
                text('INSERT INTO blog_likes (post_id, user_id, username, is_anonymous, anonymous_id, ip_address) VALUES (:post_id, :user_id, :username, :is_anonymous, :anonymous_id, :ip_address)'),
                {"post_id": post_id, "user_id": None, "username": username, "is_anonymous": True, "anonymous_id": anonymous_id, "ip_address": ip_address}
            )
            # For SQLite compatibility
            if hasattr(cursor, 'lastrowid'):
                like_id = cursor.lastrowid
            else:
                # For PostgreSQL
                like_id = cursor.fetchone()[0] if cursor.returns_rows else None
                
            conn.commit()
            return like_id
        except Exception as e:
            print(f"Error creating anonymous blog like: {e}")
            return None

class CommentLike:
    """Comment like model for managing comment likes"""
    
    @staticmethod
    def create(comment_id, user_id):
        """Create a new comment like"""
        conn = get_db_connection()
        
        # Check if like already exists for this user/comment combination
        existing = conn.execute(
            text('SELECT id FROM comment_likes WHERE comment_id = :comment_id AND user_id = :user_id'),
            {"comment_id": comment_id, "user_id": user_id}
        ).fetchone()
        
        if existing:
            return None  # User already liked this comment
        
        try:
            cursor = conn.execute(
                text('INSERT INTO comment_likes (comment_id, user_id) VALUES (:comment_id, :user_id)'),
                {"comment_id": comment_id, "user_id": user_id}
            )
            # For SQLite compatibility
            if hasattr(cursor, 'lastrowid'):
                like_id = cursor.lastrowid
            else:
                # For PostgreSQL
                like_id = cursor.fetchone()[0] if cursor.returns_rows else None
                
            conn.commit()
            return like_id
        except Exception as e:
            print(f"Error creating comment like: {e}")
            return None
    
    @staticmethod
    def delete(comment_id, user_id):
        """Delete a comment like by comment_id and user_id"""
        conn = get_db_connection()
        try:
            conn.execute(
                text('DELETE FROM comment_likes WHERE comment_id = :comment_id AND user_id = :user_id'),
                {"comment_id": comment_id, "user_id": user_id}
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting comment like: {e}")
            return False
    
    @staticmethod
    def has_user_liked(comment_id, user_id):
        """Check if a user has liked a comment"""
        conn = get_db_connection()
        result = conn.execute(
            text('SELECT id FROM comment_likes WHERE comment_id = :comment_id AND user_id = :user_id'),
            {"comment_id": comment_id, "user_id": user_id}
        ).fetchone()
        return bool(result)
    
    @staticmethod
    def get_count_for_comment(comment_id):
        """Get the count of likes for a comment"""
        conn = get_db_connection()
        result = conn.execute(
            text('SELECT COUNT(*) as count FROM comment_likes WHERE comment_id = :comment_id'),
            {"comment_id": comment_id}
        ).fetchone()
        
        # Handle different result row types (dict-like or tuple)
        if result:
            try:
                if hasattr(result, "_mapping"):
                    return result._mapping["count"]
                else:
                    # In tuple form, the count should be the first column
                    return result[0]
            except Exception as e:
                print(f"Error accessing count: {e}")
                return 0
        return 0

class CVDownload:
    """CV Download model for tracking CV downloads"""
    
    @staticmethod
    def create(reason, user_id=None, ip_address=None, email=None, is_verified=False):
        """Record a CV download"""
        conn = get_db_connection()
        try:
            is_anonymous = user_id is None
            cursor = conn.execute(
                text('INSERT INTO cv_downloads (user_id, reason, is_anonymous, ip_address, email, is_verified) VALUES (:user_id, :reason, :is_anonymous, :ip_address, :email, :is_verified)'),
                {"user_id": user_id, "reason": reason, "is_anonymous": is_anonymous, "ip_address": ip_address, "email": email, "is_verified": is_verified}
            )
            # For SQLite compatibility
            if hasattr(cursor, 'lastrowid'):
                download_id = cursor.lastrowid
            else:
                # For PostgreSQL
                download_id = cursor.fetchone()[0] if cursor.returns_rows else None
                
            conn.commit()
            return download_id
        except Exception as e:
            print(f"Error recording CV download: {e}")
            return None
    
    @staticmethod
    def get_analytics():
        """Get analytics for CV downloads"""
        conn = get_db_connection()
        try:
            # Check if we're using PostgreSQL or SQLite
            from app import app
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            # Total downloads
            result = conn.execute(text('SELECT COUNT(*) as count FROM cv_downloads')).fetchone()
            total = 0
            if result:
                try:
                    if hasattr(result, "_mapping"):
                        total = result._mapping["count"]
                    else:
                        total = result[0]
                except Exception as e:
                    print(f"Error getting CV download count: {e}")
            
            # Downloads by reason
            by_reason = []
            by_reason_rows = conn.execute(text('''
                SELECT reason, COUNT(*) as count 
                FROM cv_downloads 
                GROUP BY reason 
                ORDER BY count DESC
            ''')).fetchall()
            
            for row in by_reason_rows:
                try:
                    if hasattr(row, "_mapping"):
                        by_reason.append(dict(row._mapping))
                    else:
                        by_reason.append({"reason": row[0], "count": row[1]})
                except Exception as e:
                    print(f"Error processing reason row: {e}")
            
            # Registered vs anonymous
            by_type_result = conn.execute(text('''
                SELECT 
                    SUM(CASE WHEN is_anonymous = FALSE THEN 1 ELSE 0 END) as registered,
                    SUM(CASE WHEN is_anonymous = TRUE THEN 1 ELSE 0 END) as anonymous
                FROM cv_downloads
            ''')).fetchone()
            
            registered = 0
            anonymous = 0
            if by_type_result:
                try:
                    if hasattr(by_type_result, "_mapping"):
                        registered = by_type_result._mapping["registered"] or 0
                        anonymous = by_type_result._mapping["anonymous"] or 0
                    else:
                        registered = by_type_result[0] or 0
                        anonymous = by_type_result[1] or 0
                except Exception as e:
                    print(f"Error processing download type counts: {e}")
            
            # Recent downloads
            recent_rows = conn.execute(text('''
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
            ''')).fetchall()
            
            recent = []
            for row in recent_rows:
                try:
                    if hasattr(row, "_mapping"):
                        recent.append(dict(row._mapping))
                    else:
                        # Map tuple values to dict keys
                        recent.append({
                            "id": row[0],
                            "reason": row[1],
                            "is_anonymous": row[2],
                            "username": row[3],
                            "created_at": row[4]
                        })
                except Exception as e:
                    print(f"Error processing recent download: {e}")
            
            return {
                'total': total,
                'by_reason': by_reason,
                'registered': registered,
                'anonymous': anonymous,
                'recent': recent
            }
        except Exception as e:
            print(f"Error getting CV download analytics: {e}")
            try:
                conn.rollback()
            except:
                pass
            return {
                'total': 0,
                'by_reason': [],
                'registered': 0,
                'anonymous': 0,
                'recent': []
            }

class VisitorStat:
    """Visitor statistics model for tracking page views"""
    
    @staticmethod
    def record_visit(ip_address, page_visited, country=None):
        """Record a page visit"""
        conn = get_db_connection()
        try:
            # Clean up IP address - take only the first part if there are multiple IPs
            if ip_address and ',' in ip_address:
                # Split and take first IP, then trim whitespace
                ip_address = ip_address.split(',')[0].strip()
            
            # Truncate IP if it's too long for the database
            if ip_address and len(ip_address) > 45:
                ip_address = ip_address[:45]
            
            # Check if this IP has visited before
            is_unique = True  # Use boolean True instead of 1
            try:
                existing = conn.execute(
                    text('SELECT id FROM visitor_stats WHERE ip_address = :ip_address'),
                    {"ip_address": ip_address}
                ).fetchone()
                
                if existing:
                    is_unique = False  # Use boolean False instead of 0
            except Exception as e:
                print(f"Error checking for existing visitor: {e}")
                conn.rollback()  # Important: roll back on error
                is_unique = False  # Use boolean False instead of 0
            
            # Now insert the visitor record
            try:
                # For PostgreSQL, use RETURNING to get the ID
                is_postgres = False
                try:
                    from app import app
                    is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
                except:
                    pass

                if is_postgres:
                    # PostgreSQL version with RETURNING
                    result = conn.execute(
                        text('INSERT INTO visitor_stats (ip_address, country, page_visited, is_unique) VALUES (:ip_address, :country, :page_visited, :is_unique) RETURNING id'),
                        {"ip_address": ip_address, "country": country, "page_visited": page_visited, "is_unique": is_unique}
                    ).fetchone()
                    
                    visitor_id = result[0] if result else None
                else:
                    # SQLite version
                    cursor = conn.execute(
                        text('INSERT INTO visitor_stats (ip_address, country, page_visited, is_unique) VALUES (:ip_address, :country, :page_visited, :is_unique)'),
                        {"ip_address": ip_address, "country": country, "page_visited": page_visited, "is_unique": is_unique}
                    )
                    visitor_id = cursor.lastrowid
                
                conn.commit()
                print(f"Recorded visit with ID: {visitor_id}")
                return visitor_id
            except Exception as e:
                print(f"Error recording visitor stat: {e}")
                conn.rollback()  # Important: roll back on error
                return None
        except Exception as e:
            print(f"Error in record_visit: {e}")
            try:
                conn.rollback()  # Final fallback
            except:
                pass
            return None
    
    @staticmethod
    def get_analytics():
        """Get visitor analytics"""
        conn = get_db_connection()
        try:
            # Check if we're using PostgreSQL or SQLite
            from app import app
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            # Total page views
            result = conn.execute(text('SELECT COUNT(*) as count FROM visitor_stats')).fetchone()
            total_views = 0
            try:
                if hasattr(result, "_mapping"):
                    total_views = result._mapping["count"]
                else:
                    total_views = result[0]
            except Exception as e:
                print(f"Error getting total views: {e}")
            
            # Unique visitors
            result = conn.execute(
                text('SELECT COUNT(DISTINCT ip_address) as count FROM visitor_stats')
            ).fetchone()
            unique_visitors = 0
            try:
                if hasattr(result, "_mapping"):
                    unique_visitors = result._mapping["count"]
                else:
                    unique_visitors = result[0]
            except Exception as e:
                print(f"Error getting unique visitors: {e}")
            
            # Most visited pages with better categorization
            popular_pages_rows = conn.execute(text('''
                SELECT 
                    page_visited, 
                    COUNT(*) as count
                FROM visitor_stats
                WHERE page_visited NOT LIKE '/api/%' 
                    AND page_visited NOT LIKE '/static/%'
                    AND page_visited NOT LIKE '/analytics%'
                    AND page_visited NOT LIKE '/admin%'
                    AND page_visited NOT LIKE '/post/like/%'
                    AND page_visited NOT LIKE '/post/unlike/%'
                    AND page_visited NOT LIKE '/comment%'
                    AND page_visited NOT LIKE '/delete%'
                    AND page_visited NOT LIKE '/edit%'
                    AND page_visited NOT LIKE '/add%'
                    AND page_visited NOT LIKE '/update%'
                    AND page_visited NOT LIKE '/download_cv'
                    AND page_visited NOT LIKE '/send-verification-link'
                    AND page_visited NOT LIKE '/verify-download'
                    AND page_visited NOT LIKE '/logout'
                GROUP BY page_visited
                ORDER BY count DESC
                LIMIT 10
            ''')).fetchall()
            
            popular_pages = []
            for row in popular_pages_rows:
                try:
                    if hasattr(row, "_mapping"):
                        page_data = dict(row._mapping)
                    else:
                        page_data = {"page_visited": row[0], "count": row[1]}
                    
                    # Improve page names for better readability
                    page_path = page_data["page_visited"]
                    page_name = VisitorStat._get_friendly_page_name(page_path)
                    page_data["page_name"] = page_name
                    page_data["page_path"] = page_path
                    
                    popular_pages.append(page_data)
                except Exception as e:
                    print(f"Error processing popular page: {e}")
            
            # Views over time (last 7 days)
            if is_postgres:
                # PostgreSQL date formatting
                views_by_day_query = text('''
                    SELECT 
                        date(created_at) as date,
                        COUNT(*) as count
                    FROM visitor_stats
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                        AND page_visited NOT LIKE '/api/%' 
                        AND page_visited NOT LIKE '/static/%'
                        AND page_visited NOT LIKE '/analytics%'
                        AND page_visited NOT LIKE '/admin%'
                    GROUP BY date
                    ORDER BY date
                ''')
            else:
                # SQLite date formatting
                views_by_day_query = text('''
                    SELECT 
                        date(created_at) as date,
                        COUNT(*) as count
                    FROM visitor_stats
                    WHERE created_at >= date('now', '-7 days')
                        AND page_visited NOT LIKE '/api/%' 
                        AND page_visited NOT LIKE '/static/%'
                        AND page_visited NOT LIKE '/analytics%'
                        AND page_visited NOT LIKE '/admin%'
                    GROUP BY date
                    ORDER BY date
                ''')
            
            views_by_day_rows = conn.execute(views_by_day_query).fetchall()
            
            views_by_day = []
            for row in views_by_day_rows:
                try:
                    if hasattr(row, "_mapping"):
                        views_by_day.append(dict(row._mapping))
                    else:
                        views_by_day.append({"date": row[0], "count": row[1]})
                except Exception as e:
                    print(f"Error processing daily views: {e}")
            
            return {
                'total_views': total_views,
                'unique_visitors': unique_visitors,
                'popular_pages': popular_pages,
                'views_by_day': views_by_day
            }
        except Exception as e:
            print(f"Error getting visitor analytics: {e}")
            try:
                conn.rollback()
            except:
                pass
            # Return default empty structure instead of None
            return {
                'total_views': 0,
                'unique_visitors': 0,
                'popular_pages': [],
                'views_by_day': []
            }
    
    @staticmethod
    def _get_friendly_page_name(page_path):
        """Convert page paths to friendly names"""
        if page_path == '/':
            return 'Home Page'
        elif page_path == '/blog':
            return 'Blog'
        elif page_path == '/login':
            return 'Login Page'
        elif page_path == '/register':
            return 'Registration Page'
        elif page_path.startswith('/blog/post/'):
            # Extract post ID and try to get post title
            try:
                post_id = page_path.split('/')[-1]
                if post_id.isdigit():
                    # Try to get the post title
                    conn = get_db_connection()
                    result = conn.execute(
                        text('SELECT title FROM posts WHERE id = :post_id'),
                        {"post_id": int(post_id)}
                    ).fetchone()
                    if result:
                        if hasattr(result, "_mapping"):
                            title = result._mapping["title"]
                        else:
                            title = result[0]
                        return f'Blog Post: {title[:50]}{"..." if len(title) > 50 else ""}'
                    else:
                        return f'Blog Post #{post_id}'
                else:
                    return 'Blog Post'
            except Exception as e:
                print(f"Error getting post title: {e}")
                return 'Blog Post'
        else:
            # For any other pages, clean up the path
            clean_path = page_path.strip('/').replace('/', ' > ').title()
            return clean_path if clean_path else 'Unknown Page'

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
                text('INSERT INTO notifications (type, message, user_id, username, is_anonymous, is_read) VALUES (:type, :message, :user_id, :username, :is_anonymous, :is_read)'),
                {"type": type, "message": message, "user_id": user_id, "username": username, "is_anonymous": is_anonymous, "is_read": False}
            )
            # For SQLite compatibility
            if hasattr(cursor, 'lastrowid'):
                notification_id = cursor.lastrowid
            else:
                # For PostgreSQL
                notification_id = cursor.fetchone()[0] if cursor.returns_rows else None
                
            conn.commit()
            return notification_id
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark a notification as read"""
        conn = get_db_connection()
        try:
            conn.execute(
                text('UPDATE notifications SET is_read = :is_read WHERE id = :notification_id'),
                {"notification_id": notification_id, "is_read": True}
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    @staticmethod
    def get_recent(limit=10):
        """Get recent notifications"""
        conn = get_db_connection()
        try:
            notifications = conn.execute(text('''
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
                LIMIT :limit
            '''), {"limit": limit}).fetchall()
            
            # Convert to list of dicts with relative time
            result = []
            for notification in notifications:
                try:
                    # Handle different row types
                    notification_dict = {}
                    if hasattr(notification, "_mapping"):
                        notification_dict = dict(notification._mapping)
                    else:
                        # Create a dict manually assuming column order matches query
                        cols = ["id", "type", "message", "username", "is_anonymous", "is_read", "created_at"]
                        notification_dict = {cols[i]: notification[i] for i in range(min(len(cols), len(notification)))}
                    
                    # Calculate relative time
                    created_at = None
                    if isinstance(notification_dict['created_at'], str):
                        try:
                            created_at = datetime.strptime(notification_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            # Try another format if the first one fails
                            created_at = datetime.strptime(notification_dict['created_at'], '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        # Already a datetime object
                        created_at = notification_dict['created_at']
                    
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
                except Exception as e:
                    print(f"Error processing notification: {e}")
            
            return result
        except Exception as e:
            print(f"Error getting recent notifications: {e}")
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
        # Create different messages based on milestone type
        if count == 1:
            message = "🎉 Welcome! Your first visitor has arrived!"
        elif count == 10:
            message = "🚀 Great start! Your website has reached 10 views!"
        elif count == 50:
            message = "📈 Growing strong! 50 people have visited your site!"
        elif count == 100:
            message = "💯 Milestone achieved! Your website has been viewed 100 times!"
        elif count == 250:
            message = "🌟 Amazing progress! 250 visitors have explored your content!"
        elif count == 500:
            message = "🔥 Half a thousand! Your website has reached 500 views!"
        elif count == 1000:
            message = "🎊 Incredible! You've hit 1,000 page views!"
        elif count == 2500:
            message = "🚀 Phenomenal growth! 2,500 views and counting!"
        elif count == 5000:
            message = "💎 Outstanding! Your website has reached 5,000 views!"
        elif count == 10000:
            message = "🏆 Legendary! 10,000 views - you're making waves!"
        elif count % 10000 == 0:
            message = f"🌟 Incredible milestone! Your website has been viewed {count:,} times!"
        elif count % 5000 == 0:
            message = f"🎯 Major achievement! {count:,} views reached!"
        elif count % 1000 == 0:
            message = f"📊 Milestone alert! Your site has {count:,} total views!"
        elif count % 500 == 0:
            message = f"📈 Growing steadily! {count} views and counting!"
        else:
            # For other hundreds, use a more varied message
            messages = [
                f"🎉 Your website has been viewed {count} times!",
                f"📊 Analytics update: {count} total page views!",
                f"🚀 Traffic milestone: {count} views reached!",
                f"📈 Visitor counter: {count} views and growing!",
                f"🌟 Progress update: {count} people have visited your site!"
            ]
            import random
            message = random.choice(messages)
        
        return Notification.create(Notification.TYPE_VIEW_MILESTONE, message)
    
    @staticmethod
    def create_daily_summary_notification():
        """Create a daily summary notification with key metrics"""
        try:
            conn = get_db_connection()
            
            # Get today's stats
            from app import app
            is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            
            if is_postgres:
                today_query = text('''
                    SELECT COUNT(*) as views, COUNT(DISTINCT ip_address) as unique_visitors
                    FROM visitor_stats 
                    WHERE date(created_at) = CURRENT_DATE
                        AND page_visited NOT LIKE '/api/%' 
                        AND page_visited NOT LIKE '/static/%'
                        AND page_visited NOT LIKE '/analytics%'
                ''')
            else:
                today_query = text('''
                    SELECT COUNT(*) as views, COUNT(DISTINCT ip_address) as unique_visitors
                    FROM visitor_stats 
                    WHERE date(created_at) = date('now')
                        AND page_visited NOT LIKE '/api/%' 
                        AND page_visited NOT LIKE '/static/%'
                        AND page_visited NOT LIKE '/analytics%'
                ''')
            
            result = conn.execute(today_query).fetchone()
            
            if result:
                if hasattr(result, "_mapping"):
                    views = result._mapping["views"]
                    unique_visitors = result._mapping["unique_visitors"]
                else:
                    views = result[0]
                    unique_visitors = result[1]
                
                if views > 0:
                    message = f"📊 Daily Summary: {views} views from {unique_visitors} unique visitors today!"
                    return Notification.create(Notification.TYPE_VIEW_MILESTONE, message)
            
        except Exception as e:
            print(f"Error creating daily summary: {e}")
        
        return None
    
    @staticmethod
    def create_engagement_notification(engagement_type, details):
        """Create notifications for various engagement activities"""
        if engagement_type == 'popular_post':
            message = f"🔥 Your post '{details['title']}' is trending with {details['views']} views!"
        elif engagement_type == 'high_engagement':
            message = f"💬 Great engagement! Your post '{details['title']}' has {details['comments']} comments and {details['likes']} likes!"
        elif engagement_type == 'new_country':
            message = f"🌍 Global reach! Someone from {details['country']} visited your website!"
        elif engagement_type == 'return_visitor':
            message = f"👋 Welcome back! You have {details['count']} returning visitors today!"
        else:
            message = f"📈 Engagement update: {details}"
        
        return Notification.create(Notification.TYPE_VIEW_MILESTONE, message)

    @staticmethod
    def create_new_user_notification(username):
        """Create a notification for a new registered user"""
        message = f"{username} is now a registered user!"
        return Notification.create(Notification.TYPE_NEW_USER, message, username=username, is_anonymous=False)

class CVVerification:
    """CV Verification model for handling verification links"""
    
    @staticmethod
    def create(email, reason, token, expires_at):
        """Create a new verification entry"""
        conn = get_db_connection()
        try:
            # For PostgreSQL, use RETURNING to get the ID
            is_postgres = False
            try:
                from app import app
                is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
            except:
                pass

            if is_postgres:
                # PostgreSQL-specific version with RETURNING
                result = conn.execute(
                    text('INSERT INTO cv_verifications (email, reason, token, expires_at) VALUES (:email, :reason, :token, :expires_at) RETURNING id'),
                    {"email": email, "reason": reason, "token": token, "expires_at": expires_at}
                ).fetchone()
                
                verification_id = result[0] if result else None
            else:
                # SQLite version
                cursor = conn.execute(
                    text('INSERT INTO cv_verifications (email, reason, token, expires_at) VALUES (:email, :reason, :token, :expires_at)'),
                    {"email": email, "reason": reason, "token": token, "expires_at": expires_at}
                )
                verification_id = cursor.lastrowid
                
            conn.commit()
            print(f"Created verification ID: {verification_id}")
            return verification_id
        except Exception as e:
            print(f"Error creating verification entry: {e}")
            try:
                conn.rollback()
            except:
                pass
            return None
    
    @staticmethod
    def get_by_token(token):
        """Get verification entry by token"""
        conn = get_db_connection()
        try:
            verification = conn.execute(
                text('SELECT * FROM cv_verifications WHERE token = :token'),
                {"token": token}
            ).fetchone()
            
            if not verification:
                return None
                
            # Handle different types of result rows
            try:
                if hasattr(verification, "_mapping"):
                    return dict(verification._mapping)
                else:
                    # Create a dict manually from the row tuple
                    # Assuming columns are: id, email, reason, token, is_used, expires_at, created_at
                    columns = ["id", "email", "reason", "token", "is_used", "expires_at", "created_at"]
                    return {columns[i]: verification[i] for i in range(min(len(columns), len(verification)))}
            except Exception as e:
                print(f"Error converting verification row to dict: {e}")
                return None
        except Exception as e:
            print(f"Error getting verification by token: {e}")
            return None
    
    @staticmethod
    def mark_as_used(token):
        """Mark a verification token as used"""
        conn = get_db_connection()
        try:
            conn.execute(
                text('UPDATE cv_verifications SET is_used = :is_used WHERE token = :token'),
                {"token": token, "is_used": True}
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking verification as used: {e}")
            return False
    
    @staticmethod
    def create_verified_download(verification_id):
        """Record a verified CV download"""
        conn = get_db_connection()
        try:
            # Get the verification record
            verification = conn.execute(
                text('SELECT * FROM cv_verifications WHERE id = :verification_id'),
                {"verification_id": verification_id}
            ).fetchone()
            
            if not verification:
                return None
                
            # Create the download record
            cursor = conn.execute(
                text('INSERT INTO cv_downloads (reason, email, is_verified) VALUES (:reason, :email, :is_verified)'),
                {"reason": verification['reason'], "email": verification['email'], "is_verified": True}
            )
            # For SQLite compatibility
            if hasattr(cursor, 'lastrowid'):
                download_id = cursor.lastrowid
            else:
                # For PostgreSQL
                download_id = cursor.fetchone()[0] if cursor.returns_rows else None
                
            conn.commit()
            return download_id
        except Exception as e:
            print(f"Error creating verified download: {e}")
            return None 