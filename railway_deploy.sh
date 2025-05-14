#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Install dependencies if needed
# pip install -r requirements.txt

# Set environment variable for Flask
export FLASK_APP=app.py

# Check if the database is already initialized
echo "Checking database status..."
DB_STATUS=$(python -c '
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("DATABASE_URL not set")
    sys.exit(1)

# Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
if database_url.startswith("postgres:"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(database_url)
    with engine.connect() as connection:
        # Check total tables in public schema
        table_count_query = text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = \'public\'
        """)
        result = connection.execute(table_count_query)
        table_count = result.scalar()
        
        if table_count > 0:
            # Check core tables more specifically
            tables = ["users", "posts", "comments"]
            found_tables = []
            
            for table in tables:
                try:
                    result = connection.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    found_tables.append(table)
                except Exception:
                    pass
                    
            if len(found_tables) >= 2:
                print("initialized")
            else:
                print("empty")
        else:
            print("empty")
except Exception as e:
    print(f"error: {e}")
' || echo "error")

echo "Database status: $DB_STATUS"

if [[ "$DB_STATUS" == "initialized" ]]; then
    echo "Database already initialized with tables. Skipping migrations."
    
    # Create admin user if needed
    echo "Checking admin user..."
    python -c '
import os
from sqlalchemy import create_engine, text

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    sys.exit(1)

# Convert postgres:// to postgresql:// for SQLAlchemy 1.4+
if database_url.startswith("postgres:"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

try:
    from werkzeug.security import generate_password_hash
    engine = create_engine(database_url)
    
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    
    if admin_username and admin_email and admin_password:
        with engine.connect() as conn:
            # Check if admin exists
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = \'admin\'"))
            count = result.scalar()
            
            if count == 0:
                print("Creating admin user...")
                hashed_password = generate_password_hash(admin_password)
                conn.execute(
                    text("INSERT INTO users (username, email, password, role) VALUES (:username, :email, :password, :role)"),
                    {"username": admin_username, "email": admin_email, "password": hashed_password, "role": "admin"}
                )
                conn.commit()
                print("Admin user created")
            else:
                print("Admin user already exists")
except Exception as e:
    print(f"Error: {e}")
'
else
    # Run database migrations
    echo "Running database migrations..."
    python -m flask db upgrade
    echo "Migrations completed successfully"
fi

# Start the application
echo "Starting the application..."
exec gunicorn app:app 