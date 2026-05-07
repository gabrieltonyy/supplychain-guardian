from datetime import datetime

from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Basic API health check endpoint.
    """

    return {
        "success": True,
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes/Docker liveness probe.
    """

    return {
        "status": "alive"
    }


@router.get("/health/ready")
async def readiness_probe():
    """
    Readiness probe.
    Future:
    - DB connectivity
    - Redis connectivity
    - Qdrant readiness
    - Ollama availability
    """

    checks = {
        "api": "ready",
        "database": "pending",
        "redis": "pending",
        "qdrant": "pending",
        "llm": "pending",
    }

    return {
        "status": "ready",
        "checks": checks,
    }