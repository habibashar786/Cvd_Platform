# CVD Risk Intelligence Platform — Production Dockerfile
# Australian Healthcare Compliant | Multi-stage build

# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt \
    && pip install --no-cache-dir --user \
       fastapi uvicorn[standard] streamlit pydantic

# ── Stage 2: Runtime ──────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: non-root user
RUN groupadd -r cvdapp && useradd -r -g cvdapp -d /app cvdapp

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/cvdapp/.local

# Copy application code
COPY api.py dashboard.py orchestrator.py ./
COPY agents/ ./agents/
COPY security/ ./security/

# Copy pre-built model artifacts (from CI/CD pipeline)
COPY outputs/ ./outputs/

# Runtime env
ENV PYTHONPATH=/app
ENV PATH=/home/cvdapp/.local/bin:$PATH
ENV CVD_PLATFORM_SECRET=""
ENV LOG_LEVEL=INFO
ENV DEPLOYMENT_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Non-root
RUN chown -R cvdapp:cvdapp /app
USER cvdapp

EXPOSE 8000 8501

# Default: run FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--log-level", "info"]
