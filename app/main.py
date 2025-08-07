# app/main.py

import asyncio
import os

from fastapi import FastAPI
from .utils.scheduler import poll_services

from .database import Base, engine
from .routers import services

if os.getenv("ENV", "dev") == "dev":
    Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(services.router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_services())