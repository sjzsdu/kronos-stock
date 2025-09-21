# Lightweight Dockerfile for Kronos Stock Prediction
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# Avoid Docker here-doc for wider compatibility
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "import sys,torch;print('PyTorch version:',torch.__version__);print('CUDA available:',torch.cuda.is_available());print('Sys.path:');print('\n'.join(sys.path))"

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# (Optional) create non-root user; will stay root for now to ensure packages visible
RUN useradd -m appuser && chown -R appuser:appuser /app
# To drop privileges later, uncomment:
# USER appuser

EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:5001/api/health || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "run.py"]
