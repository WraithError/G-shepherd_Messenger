"""Chat ORM models (placeholder)."""

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    sender_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
