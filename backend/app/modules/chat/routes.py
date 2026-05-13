"""Chat HTTP routes."""

from fastapi import APIRouter
from . import service, schemas

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/messages", response_model=schemas.MessageRead)
async def send_message(msg: schemas.MessageCreate):
    return await service.create_message(msg)
