# Use the official image as a parent image
FROM python:3.8

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev build-essential libssl-dev libffi-dev

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME OPENAI_API_KEY
ENV NAME API_ID
ENV NAME API_HASH

# Run app.py when the container launches
CMD ["python", "app.py"]