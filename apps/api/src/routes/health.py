"""Health check routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="CognitiveOS API",
        version="1.0.0",
    )


@router.get("/health/ready", tags=["health"])
async def readiness_check() -> dict:
    """Kubernetes readiness probe."""
    return {"ready": True}


@router.get("/health/live", tags=["health"])
async def liveness_check() -> dict:
    """Kubernetes liveness probe."""
    return {"alive": True}
