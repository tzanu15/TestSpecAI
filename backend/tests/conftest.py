"""
Pytest configuration and fixtures for TestSpecAI backend tests.

This module provides shared fixtures and configuration for all backend tests,
including database setup, test client, and common test data.
"""

import pytest
import pytest_asyncio
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db
from app.models import Base

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    import uuid
    import time

    # Create unique database name for each test
    test_db_name = f"./test_{uuid.uuid4().hex[:8]}_{int(time.time())}.db"
    test_db_url = f"sqlite+aiosqlite:///{test_db_name}"

    # Create test engine with unique database
    test_engine_local = create_async_engine(test_db_url, echo=False)
    TestSessionLocal_local = sessionmaker(test_engine_local, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with test_engine_local.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal_local() as session:
        yield session

    # Dispose engine to release all connections
    await test_engine_local.dispose()

    # Clean up - remove test database
    try:
        if os.path.exists(test_db_name):
            os.remove(test_db_name)
    except PermissionError:
        # Database file is still locked on Windows, skip cleanup
        pass


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Create test client with database session override."""
    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_parameter_category_data():
    """Sample parameter category data for testing."""
    return {
        "name": "Test Category",
        "description": "Test category description"
    }


@pytest.fixture
def sample_parameter_data():
    """Sample parameter data for testing."""
    return {
        "name": "Test Parameter",
        "description": "Test parameter description",
        "has_variants": False,
        "default_value": "default"
    }


@pytest.fixture
def sample_parameter_with_variants_data():
    """Sample parameter with variants data for testing."""
    return {
        "name": "Test Parameter with Variants",
        "description": "Test parameter with variants description",
        "has_variants": True,
        "variants": [
            {
                "manufacturer": "BMW",
                "value": "Level 1",
                "description": "BMW Level 1"
            },
            {
                "manufacturer": "VW",
                "value": "Level 2",
                "description": "VW Level 2"
            }
        ]
    }


@pytest.fixture
def sample_parameter_variant_data():
    """Sample parameter variant data for testing."""
    return {
        "manufacturer": "BMW",
        "value": "Level 1",
        "description": "BMW Level 1"
    }
