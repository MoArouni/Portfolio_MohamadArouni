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

# Try to import the global flag if we're being imported by the app
try:
    from app import SKIP_DB_INIT
except ImportError:
    # If we're running standalone, check the environment variable
    SKIP_DB_INIT = os.environ.get('SKIP_DB_INIT', '').lower() in ('true', '1', 'yes')
    if SKIP_DB_INIT:
        print("SKIP_DB_INIT environment variable set. Database initialization will be skipped.")

# Get database URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL environment variable not set.")
    sys.exit(1)

# Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
if database_url.startswith('postgres:'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else '(masked)'}")

# Check if we should skip initialization when run directly
if __name__ == '__main__' and SKIP_DB_INIT:
    print("SKIP_DB_INIT is set. Skipping database initialization when run directly.")
    sys.exit(0)

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
    
    # Improved command splitting - properly handling SQL with nested semicolons
    # Split into separate commands but ignore semicolons inside quotes or parentheses
    commands = []
    current_command = ""
    in_string = False
    string_char = None
    for char in schema_sql:
        if char in ["'", '"'] and not (in_string and string_char != char):
            in_string = not in_string
            if in_string:
                string_char = char
            elif not in_string:
                string_char = None
        
        if char == ';' and not in_string:
            if current_command.strip():
                commands.append(current_command.strip())
            current_command = ""
        else:
            current_command += char
    
    # Add the last command if it's not empty
    if current_command.strip():
        commands.append(current_command.strip())
    
    print(f"Extracted {len(commands)} SQL commands from schema file")
    
    # Execute each command
    with engine.connect() as conn:
        for i, cmd in enumerate(commands):
            try:
                print(f"Executing command {i+1}/{len(commands)}...")
                # Print first 100 chars of command for debugging
                print(f"Command: {cmd[:100]}..." if len(cmd) > 100 else f"Command: {cmd}")
                
                conn.execute(text(cmd))
                conn.commit()
                print(f"Command {i+1} executed successfully")
            except ProgrammingError as e:
                if "already exists" in str(e):
                    print(f"Table already exists: {e}")
                else:
                    print(f"Error executing command: {e}")
                    print(f"Full command was: {cmd}")
    
    print("Schema creation complete!")
    
    # Create admin user if environment variables are set
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if admin_username and admin_email and admin_password:
        print("\nCreating admin user...")
        hashed_password = generate_password_hash(admin_password)
        
        with engine.connect() as conn:
            try:
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
            except Exception as e:
                print(f"Error with admin user: {e}")
                # Don't fail the whole initialization if admin creation fails
    else:
        print("\nWarning: Admin credentials not found in environment variables.")
        print("No admin user was created.")
    
    print("\nDatabase initialization complete!")
    
except Exception as e:
    print(f"Error during database initialization: {e}")
    sys.exit(1)

# Add this function that can be imported
def initialize_postgres_db():
    """Initialize the PostgreSQL database - returns True if successful, False otherwise"""
    try:
        # Check if we should skip initialization based on the global flag
        if SKIP_DB_INIT:
            print("SKIP_DB_INIT flag is True. Completely skipping database initialization.")
            return True
            
        # Check if DATABASE_URL is set
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("ERROR: DATABASE_URL environment variable not set.")
            return False
        
        # Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
        if database_url.startswith('postgres:'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        print(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else '(masked)'}")
        
        # Try to connect to the database with retries
        max_retries = 5
        retry_delay = 3  # seconds
        connection_successful = False
        
        for attempt in range(max_retries):
            try:
                # Create engine
                engine = create_engine(database_url)
                
                # Test connection
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    print("Database connection successful!")
                    connection_successful = True
                    break
            except OperationalError as e:
                if attempt < max_retries - 1:
                    print(f"Connection attempt {attempt+1} failed: {e}")
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("All connection attempts failed.")
                    print(f"Last error: {e}")
                    return False
        
        if not connection_successful:
            return False
            
        # Check if database is already initialized by querying information_schema
        print("Checking if database is already initialized...")
        with engine.connect() as conn:
            try:
                # Check if any tables exist in the public schema
                table_count_query = text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                result = conn.execute(table_count_query)
                table_count = result.scalar()
                
                if table_count > 0:
                    print(f"Database already has {table_count} tables. Skipping schema initialization.")
                    
                    # Check if admin user exists
                    admin_username = os.environ.get('ADMIN_USERNAME')
                    admin_email = os.environ.get('ADMIN_EMAIL')
                    admin_password = os.environ.get('ADMIN_PASSWORD')
                    
                    if admin_username and admin_email and admin_password:
                        try:
                            # Check if users table exists and if admin exists
                            admin_check = text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
                            admin_result = conn.execute(admin_check)
                            admin_count = admin_result.scalar()
                            
                            if admin_count == 0:
                                print("No admin user found. Creating admin user...")
                                hashed_password = generate_password_hash(admin_password)
                                
                                # Create admin user
                                conn.execute(
                                    text("INSERT INTO users (username, email, password, role) VALUES (:username, :email, :password, :role)"),
                                    {"username": admin_username, "email": admin_email, "password": hashed_password, "role": "admin"}
                                )
                                conn.commit()
                                print("Admin user created successfully!")
                            else:
                                print(f"Admin users already exist ({admin_count} found)")
                        except Exception as admin_error:
                            print(f"Error checking/creating admin user: {admin_error}")
                    
                    return True
            except Exception as e:
                print(f"Error checking database schema: {e}")
                # Continue to initialization if we can't check
        
        # Now create tables
        print("\nInitializing PostgreSQL database...")
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema_postgres.sql')
        if not os.path.exists(schema_path):
            print(f"ERROR: PostgreSQL schema file not found at {schema_path}")
            # Try the default schema file as a fallback
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if not os.path.exists(schema_path):
                print(f"ERROR: Fallback schema file not found at {schema_path}")
                return False
            print(f"Using fallback schema file: {schema_path}")
        else:
            print(f"Using PostgreSQL schema file: {schema_path}")
            
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Improved command splitting - properly handling SQL with nested semicolons
        # Split into separate commands but ignore semicolons inside quotes or parentheses
        commands = []
        current_command = ""
        in_string = False
        string_char = None
        for char in schema_sql:
            if char in ["'", '"'] and not (in_string and string_char != char):
                in_string = not in_string
                if in_string:
                    string_char = char
                elif not in_string:
                    string_char = None
            
            if char == ';' and not in_string:
                if current_command.strip():
                    commands.append(current_command.strip())
                current_command = ""
            else:
                current_command += char
        
        # Add the last command if it's not empty
        if current_command.strip():
            commands.append(current_command.strip())
        
        print(f"Extracted {len(commands)} SQL commands from schema file")
        
        # Execute each command
        with engine.connect() as conn:
            for i, cmd in enumerate(commands):
                try:
                    # Skip commands that might cause unique constraint violations
                    if "CREATE TABLE" in cmd:
                        table_name = cmd.split("CREATE TABLE")[1].strip().split(" ")[0].split("(")[0].strip()
                        print(f"Checking if table {table_name} already exists...")
                        try:
                            # Check if table exists before trying to create it
                            conn.execute(text(f"SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}'"))
                            result = conn.fetchone()
                            if result:
                                print(f"Table {table_name} already exists. Skipping.")
                                continue
                        except Exception as table_check_error:
                            print(f"Error checking table existence: {table_check_error}")
                    
                    # Skip index creation commands to avoid duplicate index errors
                    if "CREATE INDEX" in cmd:
                        print(f"Skipping index creation: {cmd[:100]}...")
                        continue
                        
                    print(f"Executing command {i+1}/{len(commands)}...")
                    # Print first 100 chars of command for debugging
                    print(f"Command: {cmd[:100]}..." if len(cmd) > 100 else f"Command: {cmd}")
                    
                    conn.execute(text(cmd))
                    conn.commit()
                    print(f"Command {i+1} executed successfully")
                except ProgrammingError as e:
                    if "already exists" in str(e):
                        print(f"Object already exists: {e}")
                    else:
                        print(f"Error executing command: {e}")
                        print(f"Full command was: {cmd}")
        
        print("Schema creation complete!")
        
        # Create admin user if environment variables are set
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        
        if admin_username and admin_email and admin_password:
            print("\nCreating admin user...")
            hashed_password = generate_password_hash(admin_password)
            
            with engine.connect() as conn:
                try:
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
                except Exception as e:
                    print(f"Error with admin user: {e}")
                    # Don't fail the whole initialization if admin creation fails
        else:
            print("\nWarning: Admin credentials not found in environment variables.")
            print("No admin user was created.")
        
        print("\nDatabase initialization complete!")
        return True
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        return False

# Execute script directly
if __name__ == '__main__':
    # When run directly, initialize the database and return appropriate exit code
    if initialize_postgres_db():
        sys.exit(0)
    else:
        sys.exit(1) 