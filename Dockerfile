# Base image
FROM python:3.10-slim

# Set working directory
WORKWORK /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY scripts/ scripts/

# Copy API specific requirements and install them
COPY src/api/requirements.txt api-requirements.txt
RUN pip install --no-cache-dir -r api-requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]