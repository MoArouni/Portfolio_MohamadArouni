import os
from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

# Initialize SQLAlchemy here but without app context
db = SQLAlchemy()

# Load environment variables
load_dotenv(override=True)

# Get environment variables
username = os.environ.get('ADMIN_USERNAME') or os.environ.get('username')
email = os.environ.get('ADMIN_EMAIL') or os.environ.get('email')
password = os.environ.get('ADMIN_PASSWORD') or os.environ.get('password')

def update_admin_user(conn):
    """Update the existing admin user"""
    if not username or not email or not password:
        return False
        
    hashed_password = generate_password_hash(password)
    try:
        conn.execute(
            text('UPDATE users SET username = :username, email = :email, password = :password WHERE role = :role'),
            {"username": username, "email": email, "password": hashed_password, "role": 'admin'}
        )
        return True
    except Exception as e:
        print(f"Error updating admin user: {e}")
        return False

def init_db():
    """Initialize the database"""
    from app import app
    
    with app.app_context():
        is_postgres = 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']
        is_sqlite = 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
        
        print(f"Initializing database: PostgreSQL={is_postgres}, SQLite={is_sqlite}")
        
        if not is_postgres and not is_sqlite:
            raise ValueError("Unsupported database type. Only PostgreSQL and SQLite are supported.")
        
        # Create tables from appropriate schema
        if is_postgres:
            print("Initializing PostgreSQL database...")
            # PostgreSQL requires special handling with transactions for schema creation
            schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if os.path.exists(schema_file):
                with open(schema_file) as f:
                    sql_commands = f.read()
                    # Split commands by semicolon and execute each one separately
                    for command in sql_commands.split(';'):
                        command = command.strip()
                        if command:  # Skip empty commands
                            try:
                                db.session.execute(text(command))
                                db.session.commit()
                            except Exception as e:
                                print(f"Error executing command: {e}")
                                print(f"Command was: {command}")
                                db.session.rollback()
            else:
                print(f"Warning: Schema file {schema_file} not found.")
                
        elif is_sqlite:
            print("Initializing SQLite database...")
            # For SQLite, use the schema_sqlite.sql file if it exists
            sqlite_schema = os.path.join(os.path.dirname(__file__), 'schema_sqlite.sql')
            if os.path.exists(sqlite_schema):
                print("Using SQLite-specific schema file...")
                with open(sqlite_schema) as f:
                    sql_commands = f.read()
                    # Split commands by semicolon and execute each one separately
                    for command in sql_commands.split(';'):
                        command = command.strip()
                        if command:  # Skip empty commands
                            try:
                                db.session.execute(text(command))
                                db.session.commit()
                            except Exception as e:
                                print(f"Error executing command: {e}")
                                print(f"Command was: {command}")
                                db.session.rollback()
            else:
                # Fall back to using the main schema file, which may need tweaking for SQLite
                print("Using adapted PostgreSQL schema for SQLite...")
                schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
                if os.path.exists(schema_file):
                    with open(schema_file) as f:
                        sql_commands = f.read()
                        # Convert PostgreSQL-specific syntax to SQLite
                        sql_commands = sql_commands.replace('SERIAL', 'INTEGER')
                        sql_commands = sql_commands.replace('true', '1')
                        sql_commands = sql_commands.replace('false', '0')
                        # Remove CASCADE keyword which SQLite doesn't support
                        sql_commands = sql_commands.replace('CASCADE', '')
                        
                        # Split commands by semicolon and execute each one separately
                        for command in sql_commands.split(';'):
                            command = command.strip()
                            if command:  # Skip empty commands
                                try:
                                    db.session.execute(text(command))
                                    db.session.commit()
                                except Exception as e:
                                    print(f"Error executing command: {e}")
                                    print(f"Command was: {command}")
                                    db.session.rollback()
                else:
                    print(f"Warning: Schema file {schema_file} not found.")
                
                print("WARNING: Using PostgreSQL schema for SQLite. Some features may not work correctly.")
        
        # Create admin user if none exists
        try:
            result = db.session.execute(text('SELECT COUNT(*) as count FROM users'))
            user_count = result.scalar()
            
            if user_count == 0:
                create_admin_user1()
                print("Created admin user.")
        except Exception as e:
            print(f"Error checking for users: {e}")

def create_admin_user1():
    """Create a default admin user"""
    if not username or not email or not password:
        print("Warning: Admin credentials not found in environment variables.")
        return False
        
    hashed_password = generate_password_hash(password)
    try:
        db.session.execute(
            text('INSERT INTO users (username, email, password, role) VALUES (:username, :email, :password, :role)'),
            {"username": username, "email": email, "password": hashed_password, "role": 'admin'}
        )
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.session.rollback()
        return False

def get_db_connection():
    """Get a database connection using SQLAlchemy"""
    from app import app
    
    with app.app_context():
        return db.session

# Execute script directly
if __name__ == '__main__':
    from app import app
    with app.app_context():
        init_db() 