# app/main.py

from fastapi import FastAPI

from .database import Base, engine
from .routers import services

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(services.router)
