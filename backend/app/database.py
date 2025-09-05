"""
Database configuration and connection management for TestSpecAI.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os


def get_database_url() -> str:
    """Get database URL based on environment configuration."""
    if settings.ENVIRONMENT == "development":
        # SQLite for development
        db_path = os.path.join(os.path.dirname(__file__), "..", "testspecai.db")
        return f"sqlite+aiosqlite:///{db_path}"
    else:
        # PostgreSQL for production
        if not all([settings.DB_HOST, settings.DB_USER, settings.DB_PASSWORD, settings.DB_NAME]):
            raise ValueError("Production database configuration incomplete. Please set DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME environment variables.")

        return f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT or 5432}/{settings.DB_NAME}"


# Create async engine
DATABASE_URL = get_database_url()

# Development (SQLite)
if settings.ENVIRONMENT == "development":
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}  # SQLite specific
    )
# Production (PostgreSQL)
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=30,
        pool_recycle=3600,
        pool_timeout=30
    )

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    from app.models.base import Base

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()


async def health_check() -> bool:
    """Check database connection health."""
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False
