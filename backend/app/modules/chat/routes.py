import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.chat.schemas import (
    ConversationCreate,
    ConversationOut,
    MessageOut,
)
from app.modules.chat.service import ChatService

router = APIRouter()


@router.post("/conversations", response_model=ConversationOut, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    # TODO: current_user = Depends(get_current_user) when auth is ready
    current_user_id: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001"),
    db: AsyncSession = Depends(get_db),
):
    """Create a new DM or group conversation."""
    service = ChatService(db)
    return await service.create_conversation(data, current_user_id)


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    current_user_id: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001"),
    db: AsyncSession = Depends(get_db),
):
    """Get all conversations for the current user."""
    service = ChatService(db)
    return await service.get_user_conversations(current_user_id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
async def get_message_history(
    conversation_id: uuid.UUID,
    limit: int = 50,
    before_id: uuid.UUID | None = None,
    current_user_id: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001"),
    db: AsyncSession = Depends(get_db),
):
    """
    Paginated message history.
    Pass before_id to load older messages (infinite scroll).
    """
    service = ChatService(db)
    return await service.get_history(conversation_id, current_user_id, limit, before_id)


@router.delete("/messages/{message_id}", status_code=204)
async def delete_message(
    message_id: uuid.UUID,
    current_user_id: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001"),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a message. Only the sender can delete their own."""
    service = ChatService(db)
    await service.delete_message(message_id, current_user_id)
