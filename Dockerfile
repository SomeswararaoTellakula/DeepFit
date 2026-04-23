# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Change working directory to where app.py is
WORKDIR "/app/SIH_FinalApp 2/SIH-7/HeightAndWeightCalculator"

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
# Hugging Face Spaces expect the app to run on port 7860
CMD ["python", "app.py"]
