import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('username')
email = os.getenv('email')
password = os.getenv('password')

# Debug prints to verify environment variables
print("Environment variables loaded:")
print(f"Username: {username}")
print(f"Email: {email}")
print(f"Password: {'*' * len(password) if password else None}")

# Database file path
DB_PATH = 'blog.db'

def update_admin_user(conn):
    """Update the existing admin user"""
    hashed_password = generate_password_hash(password)
    conn.execute(
        'UPDATE users SET username = ?, email = ?, password = ? WHERE role = ?',
        ('MoArouni', email, hashed_password, 'admin')
    )
    print("Admin user updated")
    print(f"Username: {username}")

def init_db():
    """Initialize the database with schema"""
    # Check if database exists
    db_exists = os.path.exists(DB_PATH)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Enable foreign keys
    conn.execute('PRAGMA foreign_keys = ON')
    
    # If database exists, check and update current admin user
    if db_exists:
        admin_user = conn.execute('SELECT username, email, role FROM users WHERE role = ?', ('admin',)).fetchone()
        if admin_user:
            print("\nCurrent admin user in database:")
            print(f"Username: {admin_user['username']}")
            print(f"Email: {admin_user['email']}")
            print(f"Role: {admin_user['role']}")
            # Update the admin user

    
    # Create tables from schema file
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    # If this is a new database, add a default admin user
    if not db_exists:
        create_admin_user(conn)
        update_admin_user(conn)
    
    conn.commit()
    conn.close()
    
    print(f"\nDatabase initialized at {DB_PATH}")

def create_admin_user(conn):
    """Create a default admin user"""
    hashed_password = generate_password_hash(password)
    conn.execute(
        'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
        ('MoArouni', email, hashed_password, 'admin')
    )
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password) if password else None}")
    print("Default admin user created")

def get_db_connection():
    """Get a database connection with row factory"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        # Re-raise to let the caller handle it
        raise

# Execute script directly
if __name__ == '__main__':
    init_db() 