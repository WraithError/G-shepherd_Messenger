import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.modules.chat.enums import ConversationType, MemberRole, MessageType, WSEventType


# ── Message Schemas ────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    conversation_id: uuid.UUID
    content: str | None = None
    type: MessageType = MessageType.TEXT
    media_url: str | None = None
    reply_to_id: uuid.UUID | None = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Message content cannot be empty")
        if v is not None and len(v) > 4096:
            raise ValueError("Message too long — max 4096 characters")
        return v


class MessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID | None
    type: MessageType
    content: str | None
    media_url: str | None
    reply_to_id: uuid.UUID | None
    is_deleted: bool
    edited_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Conversation Schemas ───────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    type: ConversationType = ConversationType.DIRECT
    name: str | None = None
    member_ids: list[uuid.UUID]

    @field_validator("name")
    @classmethod
    def name_required_for_group(cls, v: str | None, info) -> str | None:
        # Will be validated in service — schema stays thin
        return v

    @field_validator("member_ids")
    @classmethod
    def at_least_one_member(cls, v: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(v) == 0:
            raise ValueError("Conversation must have at least one other member")
        return v


class ConversationOut(BaseModel):
    id: uuid.UUID
    type: ConversationType
    name: str | None
    avatar_url: str | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Member Schemas ─────────────────────────────────────────────────────────────

class MemberOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    role: MemberRole
    joined_at: datetime
    is_muted: bool

    model_config = {"from_attributes": True}


# ── WebSocket Event Schemas ────────────────────────────────────────────────────

class WSIncomingEvent(BaseModel):
    """Shape of every message the client sends over WebSocket."""
    event: WSEventType   # Pydantic auto-converts "send_message" → WSEventType.SEND_MESSAGE
    payload: dict = {}


class WSOutgoingEvent(BaseModel):
    """Shape of every message the server sends over WebSocket."""
    event: str
    payload: dict = {}
