import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logger import get_logger
from app.modules.chat.enums import WSEventType
from app.modules.chat.manager import manager
from app.modules.chat.schemas import MessageCreate, WSIncomingEvent
from app.modules.chat.service import ChatService
from app.modules.shared.exceptions.errors import ForbiddenError, NotFoundError

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,           # TODO: replace with JWT from query param when auth is ready
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    WebSocket endpoint for a single conversation.
    One connection per user per conversation.

    Flow:
        connect → verify membership → listen for events → handle → broadcast
    """
    service = ChatService(db)

    # Fail Fast — verify membership before accepting connection
    try:
        await service.get_conversation_or_raise(conversation_id, user_id)
    except (ForbiddenError, NotFoundError) as e:
        await websocket.close(code=4003, reason=str(e))
        return

    await manager.connect(websocket, conversation_id, user_id)

    # Notify room that user came online
    await manager.broadcast_to_room(
        conversation_id,
        payload={"event": WSEventType.USER_ONLINE, "payload": {"user_id": str(user_id)}},
        exclude_user=user_id,
    )

    # Send last 50 messages as history on connect
    history = await service.get_history(conversation_id, user_id, limit=50)
    await websocket.send_json({
        "event": "history",
        "payload": {
            "messages": [
                {
                    "id": str(m.id),
                    "sender_id": str(m.sender_id) if m.sender_id else None,
                    "type": m.type,
                    "content": m.content,
                    "media_url": m.media_url,
                    "reply_to_id": str(m.reply_to_id) if m.reply_to_id else None,
                    "created_at": m.created_at.isoformat(),
                    "edited_at": m.edited_at.isoformat() if m.edited_at else None,
                }
                for m in history
            ]
        },
    })

    try:
        while True:
            raw = await websocket.receive_json()
            event = WSIncomingEvent(**raw)
            await _handle_event(event, conversation_id, user_id, service, websocket)

    except WebSocketDisconnect:
        manager.disconnect(conversation_id, user_id)
        await manager.broadcast_to_room(
            conversation_id,
            payload={"event": WSEventType.USER_OFFLINE, "payload": {"user_id": str(user_id)}},
        )
        logger.info(f"User {user_id} disconnected from {conversation_id}")

    except Exception as e:
        logger.error(f"Unexpected WS error for user {user_id}: {e}")
        manager.disconnect(conversation_id, user_id)


async def _handle_event(
    event: WSIncomingEvent,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    service: ChatService,
    websocket: WebSocket,
) -> None:
    """Route incoming WebSocket events to the right handler."""

    match event.event:

        case WSEventType.SEND_MESSAGE:
            data = MessageCreate(
                conversation_id=conversation_id,
                content=event.payload.get("content"),
                type=event.payload.get("type", "text"),
                media_url=event.payload.get("media_url"),
                reply_to_id=event.payload.get("reply_to_id"),
            )
            try:
                message = await service.send_message(data, sender_id=user_id)
                # Broadcast new message to ALL members in the room
                await manager.broadcast_to_room(
                    conversation_id,
                    payload={
                        "event": WSEventType.NEW_MESSAGE,
                        "payload": {
                            "id": str(message.id),
                            "sender_id": str(message.sender_id),
                            "type": message.type,
                            "content": message.content,
                            "media_url": message.media_url,
                            "reply_to_id": str(message.reply_to_id) if message.reply_to_id else None,
                            "created_at": message.created_at.isoformat(),
                        },
                    },
                )
            except Exception as e:
                await websocket.send_json({
                    "event": WSEventType.ERROR,
                    "payload": {"detail": str(e)},
                })

        case WSEventType.TYPING_START:
            await manager.broadcast_to_room(
                conversation_id,
                payload={"event": WSEventType.USER_TYPING, "payload": {"user_id": str(user_id)}},
                exclude_user=user_id,
            )

        case WSEventType.TYPING_STOP:
            await manager.broadcast_to_room(
                conversation_id,
                payload={"event": WSEventType.USER_STOP_TYPING, "payload": {"user_id": str(user_id)}},
                exclude_user=user_id,
            )

        case WSEventType.MARK_READ:
            message_id = event.payload.get("message_id")
            if message_id:
                await service.mark_read(conversation_id, uuid.UUID(message_id), user_id)
                await manager.broadcast_to_room(
                    conversation_id,
                    payload={
                        "event": WSEventType.MESSAGE_READ,
                        "payload": {"user_id": str(user_id), "message_id": message_id},
                    },
                    exclude_user=user_id,
                )

        case _:
            await websocket.send_json({
                "event": WSEventType.ERROR,
                "payload": {"detail": f"Unknown event: {event.event}"},
            })
