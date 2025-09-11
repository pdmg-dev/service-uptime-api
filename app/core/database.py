# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine with conditional SQLite config
engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,  # Checks connection health before using
    connect_args=(
        {"check_same_thread": False}
        if settings.database_url.startswith("sqlite")
        else {}
    ),
)

# Session factory for database interactions
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

# Base class for ORM models
Base = declarative_base()
