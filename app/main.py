# app/main.py

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import auth, dashboard, services, health
from app.services import checker
from app.services.scheduler import poll_services

# DB Initialization
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(FastAPI):
    asyncio.create_task(poll_services())
    yield
    await checker.client.aclose()


app = FastAPI(title="Service Uptime API", lifespan=lifespan)

# Routers
app.include_router(services.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(health.router)

