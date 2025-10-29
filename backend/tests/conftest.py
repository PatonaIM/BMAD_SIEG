"""
Pytest configuration and shared fixtures for testing.
"""
import asyncio
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base

# Import all models so Base.metadata knows about them
from app.models import (  # noqa: F401
    AssessmentResult,
    Candidate,
    Interview,
    InterviewMessage,
    InterviewSession,
    Resume,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        settings.test_database_url,
        poolclass=NullPool,
        connect_args={"statement_cache_size": 0},  # Supabase pgbouncer compatibility
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session for each test."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session, session.begin():
        yield session
        # Rollback will happen automatically when exiting the context


@pytest.fixture
async def test_candidate(test_db: AsyncSession):
    """Create a test candidate for authentication tests."""
    from uuid import uuid4

    from app.core.security import hash_password

    # Use a unique email for each test
    candidate = Candidate(
        id=uuid4(),
        email=f"test-{uuid4()}@example.com",
        full_name="Test User",
        password_hash=hash_password("TestPassword123!"),
        status="active"
    )
    test_db.add(candidate)
    await test_db.flush()
    await test_db.refresh(candidate)

    # Store the original email for tests that need a known value
    candidate._test_password = "TestPassword123!"
    return candidate


@pytest.fixture
async def test_client(test_db: AsyncSession):
    """Create a test client with database dependency override."""
    from httpx import ASGITransport, AsyncClient

    from app.core.database import get_db
    from main import app

    # Override the get_db dependency to use our test database session
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    # Clean up the override
    app.dependency_overrides.clear()
