from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging, get_logger
from app.api.routes.db_workflow import router as db_workflow_router


# Initialize logging first
setup_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    logger.info("Starting SupplyChain Guardian API")

    # Future startup hooks:
    # - DB connection validation
    # - Redis connectivity check
    # - Qdrant collection validation
    # - Scheduler startup
    # - LangGraph initialization

    yield

    logger.info("Shutting down SupplyChain Guardian API")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI-powered autonomous supply chain risk management platform",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register exception handlers
register_exception_handlers(app)


# Register API routes
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(db_workflow_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    """
    return {
        "success": True,
        "message": "SupplyChain Guardian API is running",
        "environment": settings.APP_ENV,
        "version": "0.1.0",
    }

