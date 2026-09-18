from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stripe import StripeClient

from api.error_handlers import register_error_handlers
from api.routes.payment import router as payment_router
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI): # pragma: no cover.
    app.state.stripe_client = StripeClient(settings.stripe_secret_key)
    app.state.http_client = httpx.AsyncClient(timeout=settings.http_timeout)
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)


register_error_handlers(app)
app.include_router(payment_router)
