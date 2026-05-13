"""ASGI entrypoint for the backend app."""

from fastapi import FastAPI

from .modules.auth.routes import router as auth_router
from .modules.chat.routes import router as chat_router

app = FastAPI(title="G Shepherds API")

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"status": "ok"}
