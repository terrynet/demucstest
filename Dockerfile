# Step 1: Use an official Python runtime as a base image
FROM python:3.10-slim

# Step 2: Set the working directory in the container
WORKDIR /usr/src/app

# Step 3: Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    sox \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy the current directory contents into the container at /usr/src/app
COPY . .

# Step 5: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Expose the port your app will run on
EXPOSE 5000

# Step 7: Run the application
CMD ["python", "app.py"]
