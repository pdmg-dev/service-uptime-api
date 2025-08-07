# app/main.py

import os
from fastapi import FastAPI

from .database import Base, engine
from .routers import services

if os.getenv("ENV", "dev") == "dev":
    Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(services.router)
