from contextlib import asynccontextmanager

from api.error_handlers import register_error_handlers
from core.config import settings
import httpx
from fastapi import FastAPI
from api.routes.assistant import router as assistant_router


@asynccontextmanager
async def lifespan(app: FastAPI): # pragma: no cover.
    app.state.http_client = httpx.AsyncClient(timeout=settings.http_timeout_cinema_service)
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

app.include_router(assistant_router)

register_error_handlers(app)