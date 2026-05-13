"""Auth business logic (placeholder)."""

from . import repository, schemas

async def create_user(user: schemas.UserCreate):
    return await repository.create_user(user)
