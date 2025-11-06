"""
Teamified Candidates Portal - Backend API
FastAPI application entrypoint
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import init_db, close_db, engine
from app.core.config import settings
from app.core.exceptions import (
    InterviewNotFoundException,
    InterviewCompletedException,
    OpenAIRateLimitException,
    ContextWindowExceededException,
)
from app.api.v1 import auth, interviews, realtime, videos, admin, job_postings, applications

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
    allow_origins=settings.allowed_origins.split(","),  # From environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(interviews.router, prefix="/api/v1")
app.include_router(realtime.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(job_postings.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")


# Error handlers for custom exceptions
@app.exception_handler(InterviewNotFoundException)
async def interview_not_found_handler(request: Request, exc: InterviewNotFoundException):
    """Handle interview not found errors"""
    logger.warning(
        "interview_not_found",
        path=request.url.path,
        error=str(exc)
    )
    return JSONResponse(
        status_code=404,
        content={
            "error": "Interview not found",
            "code": "INTERVIEW_NOT_FOUND",
            "detail": str(exc)
        }
    )


@app.exception_handler(InterviewCompletedException)
async def interview_completed_handler(request: Request, exc: InterviewCompletedException):
    """Handle attempts to interact with completed interviews"""
    logger.warning(
        "interview_completed",
        path=request.url.path,
        error=str(exc)
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": "Interview already completed",
            "code": "INTERVIEW_COMPLETED",
            "detail": str(exc)
        }
    )


@app.exception_handler(OpenAIRateLimitException)
async def openai_rate_limit_handler(request: Request, exc: OpenAIRateLimitException):
    """Handle OpenAI API rate limit errors"""
    logger.error(
        "openai_rate_limit_exceeded",
        path=request.url.path,
        error=str(exc)
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "AI service temporarily unavailable",
            "code": "RATE_LIMIT_EXCEEDED",
            "detail": "Please try again in a moment"
        },
        headers={"Retry-After": "60"}
    )


@app.exception_handler(ContextWindowExceededException)
async def context_window_exceeded_handler(request: Request, exc: ContextWindowExceededException):
    """Handle conversation context overflow errors"""
    logger.warning(
        "context_window_exceeded",
        path=request.url.path,
        error=str(exc)
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": "Conversation too long",
            "code": "CONTEXT_WINDOW_EXCEEDED",
            "detail": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=type(exc).__name__,
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_SERVER_ERROR",
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


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
