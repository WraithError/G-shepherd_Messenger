"""Chat business logic (placeholder)."""

from . import repository, schemas

async def create_message(msg: schemas.MessageCreate):
    return await repository.create_message(msg)
