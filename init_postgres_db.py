"""
Script to initialize PostgreSQL database tables
This is designed to be run directly in the production environment
"""
import os
import sys
import time
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL environment variable not set.")
    sys.exit(1)

# Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
if database_url.startswith('postgres:'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else '(masked)'}")

# Try to connect to the database
max_retries = 5
retry_delay = 3  # seconds

for attempt in range(max_retries):
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            break
    except OperationalError as e:
        if attempt < max_retries - 1:
            print(f"Connection attempt {attempt+1} failed: {e}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("All connection attempts failed.")
            print(f"Last error: {e}")
            sys.exit(1)

# Now create tables
print("\nCreating database tables...")

try:
    # Read schema file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema_postgres.sql')
    if not os.path.exists(schema_path):
        print(f"ERROR: PostgreSQL schema file not found at {schema_path}")
        # Try the default schema file as a fallback
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if not os.path.exists(schema_path):
            print(f"ERROR: Fallback schema file not found at {schema_path}")
            sys.exit(1)
        print(f"Using fallback schema file: {schema_path}")
    else:
        print(f"Using PostgreSQL schema file: {schema_path}")
        
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Split into separate commands
    commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
    
    # Execute each command
    with engine.connect() as conn:
        for i, cmd in enumerate(commands):
            try:
                print(f"Executing command {i+1}/{len(commands)}...")
                conn.execute(text(cmd))
                conn.commit()
            except ProgrammingError as e:
                if "already exists" in str(e):
                    print(f"Table already exists: {e}")
                else:
                    print(f"Error executing command: {e}")
                    print(f"Command was: {cmd[:100]}...")  # Show first 100 chars
    
    print("Schema creation complete!")
    
    # Create admin user if environment variables are set
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if admin_username and admin_email and admin_password:
        print("\nCreating admin user...")
        hashed_password = generate_password_hash(admin_password)
        
        with engine.connect() as conn:
            # Check if user already exists
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'"))
            count = result.scalar()
            
            if count > 0:
                print("Admin user already exists.")
            else:
                # Create new admin user
                conn.execute(
                    text("INSERT INTO users (username, email, password, role) VALUES (:username, :email, :password, :role)"),
                    {"username": admin_username, "email": admin_email, "password": hashed_password, "role": "admin"}
                )
                conn.commit()
                print("Admin user created successfully!")
    else:
        print("\nWarning: Admin credentials not found in environment variables.")
        print("No admin user was created.")
    
    print("\nDatabase initialization complete!")
    
except Exception as e:
    print(f"Error during database initialization: {e}")
    sys.exit(1) 