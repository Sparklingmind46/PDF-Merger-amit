# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to avoid writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set up the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the main application files
COPY main.py /app/main.py
COPY health_check.py /app/health_check.py

# Expose the port for the health check server
EXPOSE 8000

# Define the health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
    CMD curl -f http://localhost:8000 || exit 1

# Command to run both the bot and health check server
CMD python health_check.py & python main.py
