FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies (needed for OpenCV if any, though headless usually works out of the box)
# libglib2.0-0 is sometimes required by OpenCV even in headless mode
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies and gunicorn for production serving
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application
COPY . .

# Expose the application port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Run the application using Gunicorn for production and print the local URL
CMD ["sh", "-c", "echo '\\n=========================================\\n🚀 App is running!\\n👉 Click to open: http://127.0.0.1:8080\\n=========================================\\n' && exec gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 app:app"]
