FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script with error handling
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting deployment with diagnostic information:"\n\
echo "Python version: $(python --version)"\n\
echo "Working directory: $(pwd)"\n\
echo "Files in directory:"\n\
ls -la\n\
\n\
echo "Checking for database initialization..."\n\
python -c "from app import app; from db_init import init_db; app.app_context().push(); init_db()" || {\n\
  echo "Error during database initialization. Running diagnostics..."\n\
  python debug_startup.py\n\
  exit 1\n\
}\n\
\n\
echo "Starting web server..."\n\
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level debug app:app\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["/app/start.sh"] 