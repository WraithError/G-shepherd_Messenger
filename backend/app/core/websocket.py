"""WebSocket helpers and utilities."""

from fastapi import WebSocket

async def accept_ws(ws: WebSocket):
    await ws.accept()
