from fastapi import APIRouter

from app.api.v1.endpoints.compliance import router as compliance_router
from app.api.v1.endpoints.execution import router as execution_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.mitigation import router as mitigation_router
from app.api.v1.endpoints.risk import router as risk_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(risk_router)
api_router.include_router(mitigation_router)
api_router.include_router(execution_router)
api_router.include_router(compliance_router)