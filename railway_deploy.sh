#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Install dependencies if needed
# pip install -r requirements.txt

# Set environment variable for Flask
export FLASK_APP=app.py

# Run database migrations
echo "Running database migrations..."
python -m flask db upgrade

echo "Migrations completed successfully"

# Start the application
echo "Starting the application..."
exec gunicorn app:app 