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

# Create a simplified startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting application..."\n\
\n\
# Start the Flask application with Gunicorn\n\
exec gunicorn --bind 0.0.0.0:$PORT \\\n\
  --workers=2 \\\n\
  --timeout=120 \\\n\
  --access-logfile=- \\\n\
  --error-logfile=- \\\n\
  --log-level=info \\\n\
  app:app\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["/app/start.sh"] 