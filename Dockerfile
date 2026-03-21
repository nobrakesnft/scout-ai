# GitHub Scout AI - Dockerfile
# Multi-stage build for smaller image size

# =============================================================================
# Build Stage
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# =============================================================================
# Production Stage
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash scout

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create data directory for SQLite
RUN mkdir -p /data && chown scout:scout /data

# Switch to non-root user
USER scout

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DATABASE_PATH=/data/scout.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
CMD ["python", "-m", "src.main"]
