# Production Dockerfile for Aerovolt FastAPI Backend
FROM python:3.13-slim AS runner

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install curl for container health check
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root system user
RUN useradd -m -u 1000 -s /bin/bash appuser

WORKDIR /app

# Install dependencies in a clean container environment (never using host .venv)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose FastAPI service port
EXPOSE 8000

# Health check against registered health endpoint
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch ASGI production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
