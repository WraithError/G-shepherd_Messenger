"""Pydantic schemas for chat."""

from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    content: str
    sender_id: int

class MessageRead(BaseModel):
    id: int
    content: str
    sender_id: int
    created_at: datetime

    class Config:
        orm_mode = True
