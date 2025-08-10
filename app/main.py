# app/main.py

"""Entry point for the Service Uptime API application."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import auth, dashboard, health, services
from app.services import checker
from app.services.scheduler import poll_services

# Create database tables on startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(FastAPI):
    """Lifespan context manager for FastAPI."""
    asyncio.create_task(poll_services())  # Start background service polling
    yield
    await checker.client.aclose()  # Close shared HTTP client


app = FastAPI(title="Service Uptime API", lifespan=lifespan)

# Register routers
app.include_router(services.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(health.router)
