"""
Chat Repository — Database access only.

Encryption happens HERE before storing, and on read before returning.
No other layer touches raw encrypted data.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import encryption
from app.modules.chat.enums import ConversationType, MemberRole, MessageType
from app.modules.chat.models import Conversation, ConversationMember, Message


class ConversationRepository:
    """All DB queries for conversations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        result = await self._db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_direct_between(
        self, user_a: uuid.UUID, user_b: uuid.UUID
    ) -> Conversation | None:
        """Find existing DM — avoids duplicate conversations."""
        result = await self._db.execute(
            select(Conversation)
            .join(ConversationMember, ConversationMember.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.type == ConversationType.DIRECT,
                    ConversationMember.user_id == user_a,
                )
            )
        )
        conversations = result.scalars().all()
        for conv in conversations:
            member_ids = await self.get_member_ids(conv.id)
            if user_b in member_ids:
                return conv
        return None

    async def get_user_conversations(self, user_id: uuid.UUID) -> list[Conversation]:
        result = await self._db.execute(
            select(Conversation)
            .join(ConversationMember, ConversationMember.conversation_id == Conversation.id)
            .where(ConversationMember.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        type: ConversationType,
        created_by: uuid.UUID,
        name: str | None = None,
    ) -> Conversation:
        conversation = Conversation(type=type, name=name, created_by=created_by)
        self._db.add(conversation)
        await self._db.flush()
        return conversation

    async def get_member_ids(self, conversation_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self._db.execute(
            select(ConversationMember.user_id).where(
                ConversationMember.conversation_id == conversation_id
            )
        )
        return list(result.scalars().all())

    async def is_member(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        result = await self._db.execute(
            select(ConversationMember).where(
                and_(
                    ConversationMember.conversation_id == conversation_id,
                    ConversationMember.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def add_member(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        role: MemberRole = MemberRole.MEMBER,
    ) -> ConversationMember:
        member = ConversationMember(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
        )
        self._db.add(member)
        await self._db.flush()
        return member

    async def update_last_read(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID, message_id: uuid.UUID
    ) -> None:
        result = await self._db.execute(
            select(ConversationMember).where(
                and_(
                    ConversationMember.conversation_id == conversation_id,
                    ConversationMember.user_id == user_id,
                )
            )
        )
        member = result.scalar_one_or_none()
        if member:
            member.last_read_message_id = message_id


class MessageRepository:
    """All DB queries for messages. Encrypts on write, decrypts on read."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, message_id: uuid.UUID) -> Message | None:
        result = await self._db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if message:
            self._decrypt_message(message)
        return message

    async def get_history(
        self,
        conversation_id: uuid.UUID,
        limit: int = 50,
        before_id: uuid.UUID | None = None,
    ) -> list[Message]:
        """Paginated history — decrypted before returning."""
        query = (
            select(Message)
            .where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == False,
                )
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        if before_id:
            before_msg = await self.get_by_id(before_id)
            if before_msg:
                query = query.where(Message.created_at < before_msg.created_at)

        result = await self._db.execute(query)
        messages = list(result.scalars().all())

        for message in messages:
            self._decrypt_message(message)

        return list(reversed(messages))  # Chronological order

    async def create(
        self,
        conversation_id: uuid.UUID,
        sender_id: uuid.UUID | None,
        content: str | None,
        type: MessageType = MessageType.TEXT,
        media_url: str | None = None,
        reply_to_id: uuid.UUID | None = None,
    ) -> Message:
        # Encrypt before storing — nothing plaintext ever touches the DB
        encrypted_content = encryption.encrypt(content) if content else None

        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=encrypted_content,
            type=type,
            media_url=media_url,
            reply_to_id=reply_to_id,
        )
        self._db.add(message)
        await self._db.flush()

        # Return plaintext to caller — they never deal with encrypted data
        message.content = content
        return message

    async def soft_delete(self, message_id: uuid.UUID, requestor_id: uuid.UUID) -> bool:
        message = await self.get_by_id(message_id)
        if not message or message.sender_id != requestor_id:
            return False
        message.is_deleted = True
        return True

    async def mark_edited(self, message_id: uuid.UUID, new_content: str) -> Message | None:
        message = await self.get_by_id(message_id)
        if not message:
            return None
        message.content = encryption.encrypt(new_content)
        message.edited_at = datetime.now(timezone.utc)
        message.content = new_content  # Return decrypted
        return message

    # ── Private ────────────────────────────────────────────────────────────────

    def _decrypt_message(self, message: Message) -> None:
        """Decrypt message content in-place. Never crashes the app."""
        if message.content:
            try:
                message.content = encryption.decrypt(message.content)
            except ValueError:
                message.content = "[message could not be decrypted]"
