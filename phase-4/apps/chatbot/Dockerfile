# Gordon-enabled Todo Chatbot
# Multi-stage build with cagent installation

# ============================================================================
# Builder Stage - Install cagent and Python dependencies
# ============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install curl and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install cagent (Docker Gordon Agent) - Latest version
RUN curl -fsSL -o /usr/local/bin/cagent \
    https://github.com/docker/cagent/releases/download/v1.20.0/cagent-linux-amd64 && \
    chmod +x /usr/local/bin/cagent

# Copy requirements and install Python deps
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================================================
# Runtime Stage - Minimal production image
# ============================================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy cagent from builder
COPY --from=builder /usr/local/bin/cagent /usr/local/bin/cagent

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Create non-root user
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser -s /sbin/nologin -c "Application user" appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser cagent-config.yaml .
COPY --chown=appuser:appuser src src

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8001", \
     "--workers", "1", \
     "--log-level", "info"]
