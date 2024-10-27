# Use the official Python image from Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose port 8501 (Streamlit's default port)
EXPOSE 8501

# Command to run your application
CMD ["streamlit", "run", "your_script_name.py", "--server.port=8080", "--server.enableCORS=false"]

