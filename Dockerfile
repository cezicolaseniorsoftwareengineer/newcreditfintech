FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ app/

# Create directory for SQLite persistence
RUN mkdir -p /app/data

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose application port
EXPOSE 8000

# Application entrypoint
# Use shell form to allow variable expansion of $PORT provided by Render
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
