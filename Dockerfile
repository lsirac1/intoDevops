# Use official Python 3.11 slim image as base
FROM python:3.11-slim

# Update all packages to latest versions as part of build
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (layer caching optimization)
COPY requirements.txt .

# Install all required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Expose port 5000 TCP (Flask default)
EXPOSE 5000

# Configure the correct command to start the Flask application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
