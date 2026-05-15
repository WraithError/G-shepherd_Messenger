import uuid
from collections import defaultdict

from fastapi import WebSocket

from app.core.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manages all active WebSocket connections.

    Structure:
        _rooms: { conversation_id → { user_id → WebSocket } }
        _user_rooms: { user_id → set of conversation_ids }

    Singleton — one instance shared across the entire app.
    """

    def __init__(self) -> None:
        # room_id → { user_id → websocket }
        self._rooms: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        # user_id → set of room_ids they're in
        self._user_rooms: dict[str, set[str]] = defaultdict(set)

    # ── Connection lifecycle ───────────────────────────────────────────────────

    async def connect(
        self,
        websocket: WebSocket,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await websocket.accept()
        room = str(conversation_id)
        uid = str(user_id)

        self._rooms[room][uid] = websocket
        self._user_rooms[uid].add(room)

        logger.info(f"User {uid} connected to room {room}")

    def disconnect(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        room = str(conversation_id)
        uid = str(user_id)

        self._rooms[room].pop(uid, None)
        self._user_rooms[uid].discard(room)

        # Clean up empty rooms — pop avoids KeyError if already cleaned
        if not self._rooms[room]:
            self._rooms.pop(room, None)

        logger.info(f"User {uid} disconnected from room {room}")

    # ── Sending ────────────────────────────────────────────────────────────────

    async def broadcast_to_room(
        self,
        conversation_id: uuid.UUID,
        payload: dict,
        exclude_user: uuid.UUID | None = None,
    ) -> None:
        """Send payload to all users in a room, optionally skipping the sender."""
        room = str(conversation_id)
        exclude = str(exclude_user) if exclude_user else None
        dead_connections: list[str] = []

        for uid, ws in self._rooms.get(room, {}).items():
            if uid == exclude:
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                # Dead socket — mark for cleanup
                dead_connections.append(uid)
                logger.warning(f"Dead connection found for user {uid} in room {room}")

        # Clean up dead connections
        for uid in dead_connections:
            self._rooms[room].pop(uid, None)

    async def send_to_user(
        self,
        user_id: uuid.UUID,
        payload: dict,
    ) -> None:
        """Send to a specific user across ALL their active rooms."""
        uid = str(user_id)
        for room in self._user_rooms.get(uid, set()):
            ws = self._rooms.get(room, {}).get(uid)
            if ws:
                try:
                    await ws.send_json(payload)
                except Exception:
                    logger.warning(f"Failed to send to user {uid} in room {room}")

    # ── Status ─────────────────────────────────────────────────────────────────

    def is_online(self, user_id: uuid.UUID) -> bool:
        return bool(self._user_rooms.get(str(user_id)))

    def get_online_users(self, conversation_id: uuid.UUID) -> list[str]:
        return list(self._rooms.get(str(conversation_id), {}).keys())


# Singleton instance — imported everywhere
manager = ConnectionManager()
