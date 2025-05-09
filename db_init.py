import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database file path
DB_PATH = 'blog.db'

def init_db():
    """Initialize the database with schema"""
    # Check if database exists
    db_exists = os.path.exists(DB_PATH)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Enable foreign keys
    conn.execute('PRAGMA foreign_keys = ON')
    
    # Create tables from schema file
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    # If this is a new database, add a default admin user
    if not db_exists:
        create_admin_user(conn)
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at {DB_PATH}")

def create_admin_user(conn):
    """Create a default admin user"""
    hashed_password = generate_password_hash('admin123')
    conn.execute(
        'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
        ('admin', 'admin@example.com', hashed_password, 'admin')
    )
    print("Default admin user created")

def get_db_connection():
    """Get a database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Execute script directly
if __name__ == '__main__':
    init_db() 