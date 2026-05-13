"""Repository layer for auth (placeholder implementations)."""

from typing import Any

async def create_user(user: Any):
    # TODO: implement DB persistence
    return {"id": 1, "email": getattr(user, "email", None), "is_active": True}
