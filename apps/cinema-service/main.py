from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from temporalio.client import Client

from api.routes.cinema import router as cinema_router
from api.routes.hall import router as hall_router
from api.error_handlers import register_error_handlers
from api.routes.health import router as health_router
from api.routes.movie import router as movie_router
from api.routes.screening import router as screening_router
from api.routes.reservation import router as reservation_router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI): # pragma: no cover.
    app.state.tmdb = httpx.AsyncClient(timeout=settings.http_timeout)
    app.state.temporal_client = await Client.connect(settings.temporal_address)
    yield
    await app.state.tmdb.aclose()

app = FastAPI(lifespan=lifespan)

register_error_handlers(app)
app.include_router(cinema_router)
app.include_router(health_router)
app.include_router(hall_router)
app.include_router(movie_router)
app.include_router(screening_router)
app.include_router(reservation_router)
