from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from openai import AsyncOpenAI
from redis.asyncio import from_url

from api.error_handlers import register_error_handlers
from api.routes.assistant import router as assistant_router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI): # pragma: no cover.
    app.state.http_client = httpx.AsyncClient(timeout=settings.http_timeout_cinema_service)
    app.state.openai_client = AsyncOpenAI(
        api_key=settings.openai_api_key, timeout=settings.http_timeout_open_api, max_retries=settings.max_retries
    )
    app.state.redis_client = from_url(url=settings.redis_url, decode_responses=True)
    yield
    await app.state.http_client.aclose()
    await app.state.openai_client.close()
    await app.state.redis_client.aclose()

app = FastAPI(lifespan=lifespan)

app.include_router(assistant_router)

register_error_handlers(app)