# app/main.py
"""Entry point for the Service Uptime API application."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import auth, dashboard, health, service, ws_dashboard
from app.services import checker
from app.services.scheduler import poll_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # start background polling and keep a reference to cancel later
    scheduler_task = asyncio.create_task(poll_services())  # store reference
    app.state.scheduler_task = scheduler_task  # save in app.state

    try:
        yield
    finally:
        # cancel scheduler first so it stops cleanly
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

        # close the shared HTTP client
        await checker.client.aclose()  # <<< existing, but now after cancel


app = FastAPI(title="Service Uptime API", lifespan=lifespan)

# Register routers
app.include_router(service.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(health.router)
app.include_router(ws_dashboard.router)
