FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for scikit-surprise
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies in correct order
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir "cython>=3.0.0" "numpy>=1.26.0,<2.0.0"
RUN pip install --no-cache-dir scikit-surprise==1.1.4
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY train.py .

# Copy models directory if exists (ignore if not)
COPY model[s]/ ./models/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
