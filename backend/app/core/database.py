"""Database configuration and connection management."""
from collections.abc import AsyncGenerator
import logging
import ssl
from contextlib import asynccontextmanager

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)

# Determine pool configuration based on environment
# For Supabase, use aggressive connection recycling to prevent exhaustion
_pool_config = {
    "pool_size": 2,              # Minimal base pool (Supabase free tier ~15 connection limit)
    "max_overflow": 3,           # Max 5 total connections (conservative for safety)
    "pool_pre_ping": True,       # Verify connection health before use
    "pool_recycle": 300,         # Recycle connections every 5 minutes
    "pool_timeout": 30,          # Wait up to 30s for connection from pool
    "echo": False,               # Set to True for SQL debugging
}

# For development with frequent restarts, consider NullPool to avoid stale connections
# Uncomment below if experiencing connection issues during development
# _pool_config["poolclass"] = NullPool

# Create async engine with optimized pooling for Supabase Transaction Pooler
engine = create_async_engine(
    settings.database_url,
    **_pool_config,
    connect_args={
        "statement_cache_size": 0,  # CRITICAL: Disable prepared statements for Transaction pooler
        "prepared_statement_cache_size": 0,  # Also disable this cache
        "server_settings": {
            "application_name": "teamified_backend",
            "jit": "off"  # Disable JIT compilation for pooler compatibility
        },
        "timeout": 20,              # Connection timeout (aggressive for fast failure)
        "command_timeout": 60,      # Query execution timeout
        "ssl": "prefer"             # Use SSL without strict certificate verification
    }
)

# Log pool statistics for monitoring
@event.listens_for(engine.sync_engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log successful connections for debugging."""
    logger.debug("Database connection established")

@event.listens_for(engine.sync_engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Log connection closures for debugging."""
    logger.debug("Database connection closed")

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
    FastAPI dependency for database sessions with proper cleanup.
    
    Ensures connections are always returned to the pool, even on errors.

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()  # Commit any pending changes
    except Exception:
        await session.rollback()  # Rollback on error
        raise
    finally:
        await session.close()  # Always close to return connection to pool


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
    """
    Gracefully close all database connections on application shutdown.
    
    This ensures all connections are properly released back to Supabase,
    preventing connection leaks that exhaust the connection pool.
    """
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed successfully")


async def get_pool_status() -> dict:
    """
    Get current connection pool statistics for monitoring.
    
    Returns:
        dict: Pool statistics including size, checked out connections, etc.
        
    Example:
        status = await get_pool_status()
        print(f"Active connections: {status['checked_out']}/{status['size']}")
    """
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "checked_in": pool.checkedin(),
    }


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions outside of FastAPI dependency injection.
    
    Use this for background tasks, CLI scripts, or anywhere you need a DB session
    outside of a FastAPI route handler.
    
    Example:
        async with get_db_context() as db:
            user = await db.get(User, user_id)
            user.name = "Updated"
            await db.commit()
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
