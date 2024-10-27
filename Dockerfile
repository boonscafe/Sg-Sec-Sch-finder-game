# Use an official Python image as a base
FROM python:3.11-slim

# Install necessary OS dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your application code
COPY . /app
WORKDIR /app

# Set environment variables for ChromaDB (optional)
# ENV CHROMA_DB_STORAGE=memory

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
