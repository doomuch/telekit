# Use the official image as a parent image
FROM python:3.9

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev build-essential libssl-dev libffi-dev ffmpeg

# Copy the current directory contents into the container at /app
COPY . /app

# Create necessary directories
RUN mkdir -p /app/data

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv
RUN pip install pydub

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variables
ENV NAME OPENAI_API_KEY
ENV NAME API_ID
ENV NAME API_HASH

# Run app.py when the container launches
CMD ["python", "app.py"]