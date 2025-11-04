"""Database configuration and connection management."""
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create async engine with connection pooling
# IMPORTANT: Using small pool sizes to avoid exhausting Supabase Session Pooler limits
# Supabase Session mode has hard limit on concurrent connections
engine = create_async_engine(
    settings.database_url,
    pool_size=3,            # Small base pool (Supabase free tier limit)
    max_overflow=7,         # Total 10 connections max
    pool_pre_ping=True,     # Health checks before using connection
    pool_recycle=300,       # Recycle connections after 5 minutes (prevent stale)
    pool_timeout=10,        # Timeout after 10s if no connection available
    echo=False,             # Set to True for SQL logging
    connect_args={
        "statement_cache_size": 0,  # Required for pgbouncer compatibility
        "server_settings": {
            "application_name": "teamified_backend",
            "jit": "off"  # Disable JIT for connection pooler
        }
    }
)

# Session factory for creating database sessions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent detached instance errors
    autoflush=False,
    autocommit=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection on application startup.

    Note: Tables are created via Alembic migrations, not here.
    This function verifies the connection is working.
    """
    async with engine.begin() as conn:
        # Test connection
        await conn.execute(text("SELECT 1"))


async def close_db() -> None:
    """Close database connections on application shutdown."""
    await engine.dispose()
