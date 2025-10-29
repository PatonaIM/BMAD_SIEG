"""
Teamified Candidates Portal - Backend API
FastAPI application entrypoint
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import init_db, close_db, engine
from app.api.v1 import auth, interviews

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan event handler"""
    # Startup
    logger.info("application_startup", version="1.0.0", environment="development")
    try:
        await init_db()
        logger.info("database_initialized", message="Database connection established")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("application_shutdown", message="Closing database connections")
    await close_db()
    logger.info("application_shutdown_complete")


# Create FastAPI application
app = FastAPI(
    title="Teamified Candidates Portal API",
    description="AI-powered technical interview platform for recruitment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(interviews.router, prefix="/api/v1")


@app.get("/health", response_model=dict[str, Any])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint
    Returns application status, version, and database connectivity
    """
    database_status = "disconnected"
    try:
        # Test database connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception as e:
        logger.error("health_check_database_error", error=str(e))
        database_status = "disconnected"
    
    return {
        "status": "healthy" if database_status == "connected" else "degraded",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database_status": database_status,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
