import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Get environment variables
username = os.getenv('USERNAME') or os.getenv('username')
email = os.getenv('EMAIL') or os.getenv('email')
password = os.getenv('PASSWORD') or os.getenv('password')

# Database file path
DB_PATH = 'blog.db'

def update_admin_user(conn):
    """Update the existing admin user"""
    if not username or not email or not password:
        return False
        
    hashed_password = generate_password_hash(password)
    try:
        conn.execute(
            'UPDATE users SET username = ?, email = ?, password = ? WHERE role = ?',
            (username, email, hashed_password, 'admin')
        )
        return True
    except sqlite3.Error:
        return False

def init_db():
    """Initialize the database"""
    # Check if database exists
    db_exists = os.path.exists(DB_PATH)
    
    # Connect to database
    conn = get_db_connection()
    
    if not db_exists:
        # Create tables if database doesn't exist
        with open('schema.sql') as f:
            conn.executescript(f.read())
        
        # Create admin user
        create_admin_user1(conn)
    else:
        # Database exists, update admin user
        update_admin_user(conn)
    
    conn.commit()
    conn.close()

def create_admin_user1(conn):
    """Create a default admin user"""
    hashed_password = generate_password_hash(password)
    conn.execute(
        'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
        (username, email, hashed_password, 'admin')
    )

def get_db_connection():
    """Get a database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Execute script directly
if __name__ == '__main__':
    init_db() 