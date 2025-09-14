# Multi-stage Dockerfile for Kronos Stock Prediction
# Build: docker build -t kronos-stock .

# Build stage - for installing dependencies and cleaning up
FROM python:3.12-slim as builder

ENV PYTHONUNBUFFERED=1
WORKDIR /build

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage - minimal runtime image
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:5001/api/health || exit 1

CMD ["python", "app.py"]
