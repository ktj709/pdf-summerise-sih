# Use lightweight Python image
FROM python:3.11-slim

# Install system dependencies: Tesseract + OpenCV libs
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Render will override with $PORT)
EXPOSE 10000

# Start FastAPI with uvicorn (host 0.0.0.0, port from Render)
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "10000"]
