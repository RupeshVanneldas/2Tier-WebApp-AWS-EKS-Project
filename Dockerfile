# Start from an official Python image
FROM python:3.8-slim-buster

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies and clean up apt cache in a single RUN command
RUN apt-get update -y && apt-get install -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of your application
COPY . /app

# Create necessary directories
RUN mkdir -p uploads

# Expose port
EXPOSE 81

# Set entrypoint to run the app
CMD ["python3", "app.py"]
