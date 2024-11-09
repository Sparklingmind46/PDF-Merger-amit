# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to avoid writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set up the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port for the application if needed
EXPOSE 8080

# Set the Koyeb health check file if applicable
# (Update "healthcheck.py" with the correct file name if different)
COPY healthcheck.py /app/healthcheck.py

# Define the health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
    CMD python healthcheck.py || exit 1

# Command to run the bot
CMD ["python", "main.py"]
