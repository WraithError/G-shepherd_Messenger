import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.enums import ConversationType, MemberRole, MessageType
from app.modules.chat.models import Conversation, Message
from app.modules.chat.repository import ConversationRepository, MessageRepository
from app.modules.chat.schemas import ConversationCreate, MessageCreate
from app.modules.shared.exceptions.errors import (
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


class ChatService:
    """
    All chat business rules live here.
    Routes call this. This calls repository.
    Never talks to DB directly.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._conv_repo = ConversationRepository(db)
        self._msg_repo = MessageRepository(db)

    # ── Conversations ──────────────────────────────────────────────────────────

    async def create_conversation(
        self, data: ConversationCreate, current_user_id: uuid.UUID
    ) -> Conversation:
        # Rule: Group chats must have a name
        if data.type == ConversationType.GROUP and not data.name:
            raise ValidationError("Group conversations must have a name")

        # Rule: Direct messages can only have exactly one other member
        if data.type == ConversationType.DIRECT:
            if len(data.member_ids) != 1:
                raise ValidationError("Direct messages must have exactly one recipient")

            # Rule: No duplicate DMs — reuse existing one
            existing = await self._conv_repo.get_direct_between(
                current_user_id, data.member_ids[0]
            )
            if existing:
                return existing

        conversation = await self._conv_repo.create(
            type=data.type,
            created_by=current_user_id,
            name=data.name,
        )

        # Creator gets owner role
        await self._conv_repo.add_member(
            conversation.id, current_user_id, role=MemberRole.OWNER
        )

        # Add all other members
        for member_id in data.member_ids:
            await self._conv_repo.add_member(conversation.id, member_id)

        return conversation

    async def get_user_conversations(
        self, user_id: uuid.UUID
    ) -> list[Conversation]:
        return await self._conv_repo.get_user_conversations(user_id)

    async def get_conversation_or_raise(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Conversation:
        conversation = await self._conv_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError("Conversation not found")

        # Rule: Only members can access a conversation
        is_member = await self._conv_repo.is_member(conversation_id, user_id)
        if not is_member:
            raise ForbiddenError("You are not a member of this conversation")

        return conversation

    # ── Messages ───────────────────────────────────────────────────────────────

    async def send_message(
        self, data: MessageCreate, sender_id: uuid.UUID
    ) -> Message:
        # Rule: Sender must be a member
        is_member = await self._conv_repo.is_member(data.conversation_id, sender_id)
        if not is_member:
            raise ForbiddenError("You are not a member of this conversation")

        # Rule: Text messages must have content
        if data.type == MessageType.TEXT and not data.content:
            raise ValidationError("Text messages require content")

        # Rule: Media messages must have a URL
        if data.type in (MessageType.IMAGE, MessageType.AUDIO, MessageType.VIDEO, MessageType.FILE):
            if not data.media_url:
                raise ValidationError(f"{data.type} messages require a media URL")

        message = await self._msg_repo.create(
            conversation_id=data.conversation_id,
            sender_id=sender_id,
            content=data.content,
            type=data.type,
            media_url=data.media_url,
            reply_to_id=data.reply_to_id,
        )

        return message

    async def get_history(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 50,
        before_id: uuid.UUID | None = None,
    ) -> list[Message]:
        # Rule: Only members can read history
        await self.get_conversation_or_raise(conversation_id, user_id)

        return await self._msg_repo.get_history(
            conversation_id=conversation_id,
            limit=min(limit, 100),  # Hard cap — no one gets 10k messages at once
            before_id=before_id,
        )

    async def delete_message(
        self, message_id: uuid.UUID, requestor_id: uuid.UUID
    ) -> None:
        deleted = await self._msg_repo.soft_delete(message_id, requestor_id)
        if not deleted:
            raise ForbiddenError("Message not found or you do not own it")

    async def mark_read(
        self,
        conversation_id: uuid.UUID,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await self._conv_repo.update_last_read(conversation_id, user_id, message_id)
