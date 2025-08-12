# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory for models
RUN mkdir -p /app/.cache

# Expose port
EXPOSE 8502

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

# Run the application
CMD ["python", "app.py"]
