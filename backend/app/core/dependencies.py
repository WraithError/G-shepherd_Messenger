"""Dependency injection helpers."""

from .database import get_db

async def get_db_dep():
    async for db in get_db():
        yield db
