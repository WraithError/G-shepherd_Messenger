"""WebSocket handlers for chat (placeholder)."""

from fastapi import WebSocket

async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"echo: {data}")
    except Exception:
        await ws.close()
