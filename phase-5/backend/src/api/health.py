"""
Health Check Endpoints - Phase 5
"""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import httpx

from src.models.base import get_db
from src.utils.config import settings
from src.utils.logging import get_logger
from src.utils.metrics import get_metrics, initialize_app_info

logger = get_logger(__name__)

router = APIRouter(tags=["health"])

# Initialize app info on import
initialize_app_info(version=settings.app_version, environment=settings.app_env)


@router.get("/health")
async def health_check():
    """
    Health check endpoint (liveness probe)
    Returns whether the service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "phase-5-backend",
        "version": settings.app_version,
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check endpoint
    Returns whether the service is ready to accept traffic
    Checks: Database, Dapr, Ollama
    """
    components = {
        "database": "unknown",
        "dapr": "unknown",
        "ollama": "unknown",
    }

    all_healthy = True

    # Check database
    try:
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        components["database"] = "healthy"
        logger.info("database_health_check_pass")
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        components["database"] = f"unhealthy: {str(e)}"
        all_healthy = False

    # Check Dapr sidecar
    try:
        dapr_port = settings.dapr_http_port or 3500
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"http://localhost:{dapr_port}/v1.0/healthz")
            if response.status_code == 200:
                components["dapr"] = "healthy"
                logger.info("dapr_health_check_pass")
            else:
                raise Exception(f"Dapr returned {response.status_code}")
    except Exception as e:
        logger.error("dapr_health_check_failed", error=str(e))
        components["dapr"] = f"unhealthy: {str(e)}"
        all_healthy = False

    # Check Ollama (optional - non-blocking)
    try:
        ollama_url = settings.ollama_url or "http://localhost:11434"
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            if response.status_code == 200:
                components["ollama"] = "healthy"
                logger.info("ollama_health_check_pass")
            else:
                components["ollama"] = f"degraded: returned {response.status_code}"
    except Exception as e:
        logger.warning("ollama_health_check_failed", error=str(e))
        components["ollama"] = f"unavailable: {str(e)}"
        # Ollama is optional, don't fail readiness

    overall_status = "ready" if all_healthy else "not_ready"

    return {
        "status": overall_status,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
    }


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Exposes all application metrics in Prometheus format.
    Includes:
    - HTTP request metrics
    - Business metrics (tasks, reminders, etc.)
    - Database metrics
    - Kafka/Dapr metrics
    - WebSocket metrics
    - AI/ML metrics
    """
    return get_metrics()
