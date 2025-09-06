"""
TestSpecAI FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, close_db, health_check
from app.api import requirements, test_specs, parameters, commands

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Automotive Test Specification AI Platform",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(requirements.router, prefix="/api/v1/requirements", tags=["requirements"])
app.include_router(test_specs.router, prefix="/api/v1/test-specifications", tags=["test-specifications"])
app.include_router(parameters.router, prefix="/api/v1/parameters", tags=["parameters"])
app.include_router(commands.router, prefix="/api/v1/commands", tags=["commands"])


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint."""
    db_healthy = await health_check()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database": "connected" if db_healthy else "disconnected"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    await close_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
