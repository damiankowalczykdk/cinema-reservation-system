from contextlib import asynccontextmanager

import httpx
from api.error_handlers import register_error_handlers
from api.routes.payment import router as payment_router
from core.config import settings
from fastapi import FastAPI
from stripe import StripeClient
from temporalio.client import Client


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover.
    app.state.stripe_client = StripeClient(settings.stripe_secret_key)
    app.state.http_client = httpx.AsyncClient(timeout=settings.http_timeout)
    app.state.temporal_client = await Client.connect(settings.temporal_address)
    yield
    await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)


register_error_handlers(app)
app.include_router(payment_router)
