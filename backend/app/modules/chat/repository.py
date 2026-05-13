"""Repository layer for chat (placeholder implementations)."""

from typing import Any

async def create_message(msg: Any):
    # TODO: persist message to DB
    return {"id": 1, "content": getattr(msg, "content", ""), "sender_id": getattr(msg, "sender_id", None), "created_at": None}
