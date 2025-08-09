# app/main.py

import asyncio
import os
import logging

from fastapi import FastAPI

from .database import Base, engine
from .routers import services
from .utils.scheduler import poll_services
from .routers import auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

if os.getenv("ENV", "dev") == "dev":
    Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(services.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_services())