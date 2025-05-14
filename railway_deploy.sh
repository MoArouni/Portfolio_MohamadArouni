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
python -c '
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
        # Check if key tables exist
        tables = ["users", "posts", "comments"]
        found_tables = []
        
        for table in tables:
            try:
                result = connection.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                found_tables.append(table)
            except Exception:
                pass
                
        if len(found_tables) >= 2:
            print(f"Database appears to be initialized (found {len(found_tables)} core tables)")
        else:
            print(f"Database needs initialization (found only {len(found_tables)} core tables)")
except Exception as e:
    print(f"Error checking database: {e}")
'

# Run database migrations
echo "Running database migrations..."
python -m flask db upgrade

echo "Migrations completed successfully"

# Start the application
echo "Starting the application..."
exec gunicorn app:app 