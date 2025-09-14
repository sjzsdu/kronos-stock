# Simple Dockerfile for csweb application
# Build from csweb directory: docker build -t kronos-csweb .

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install huggingface_hub for model downloading
RUN pip install --no-cache-dir huggingface_hub

# Copy application code
COPY . .

# Download models during build (only if not already present)
RUN python download_models.py

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:5001/api/health || exit 1

CMD ["python", "app.py"]
