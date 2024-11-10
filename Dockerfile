# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot files and the health_check.py to the container
COPY . .

# Set environment variable for unbuffered logging
ENV PYTHONUNBUFFERED=1

# Expose the port for Flask health check
EXPOSE 8000

# Command to run both Flask and the bot (using a script or supervisor)
CMD ["sh", "-c", "python health_check.py & python main.py"]
