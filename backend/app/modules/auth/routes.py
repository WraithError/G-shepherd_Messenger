"""Auth HTTP routes."""

from fastapi import APIRouter, HTTPException
from . import service, schemas

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserRead)
async def register(user: schemas.UserCreate):
    created = await service.create_user(user)
    if not created:
        raise HTTPException(status_code=400, detail="Could not create user")
    return created
