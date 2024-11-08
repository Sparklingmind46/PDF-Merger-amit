# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the bot script
COPY bot.py .

# Set the command to run the bot
CMD ["python", "bot.py"]
