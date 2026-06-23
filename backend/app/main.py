from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"🔥 {settings.APP_NAME} starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables ready")
    yield
    # Shutdown
    logger.info("🛑 Shutting down...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Loyal. Protective. Built for Uzbekistan.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,   # Hide docs in production
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


# Routers go here as modules are built:
# from app.modules.auth.routes import router as auth_router
# from app.modules.chat.routes import router as chat_router
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
