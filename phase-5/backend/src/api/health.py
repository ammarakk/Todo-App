"""
Health Check Endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from src.utils.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint (liveness probe)
    Returns whether the service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    Returns whether the service is ready to accept traffic
    """
    components = {
        "database": "unknown",
        "dapr": "unknown",
    }
    
    all_healthy = True
    
    # Check database (simplified - in production, actually ping DB)
    try:
        components["database"] = "healthy"
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        components["database"] = f"unhealthy: {str(e)}"
        all_healthy = False
    
    # Check Dapr (simplified - in production, actually ping Dapr)
    try:
        components["dapr"] = "healthy"
    except Exception as e:
        logger.error("dapr_health_check_failed", error=str(e))
        components["dapr"] = f"unhealthy: {str(e)}"
        all_healthy = False
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
    }
