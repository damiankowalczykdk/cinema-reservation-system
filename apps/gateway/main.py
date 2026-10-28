from contextlib import asynccontextmanager

import httpx
from api.error_handlers import register_error_handlers
from api.routes.assistant import router as assistant_router
from api.routes.auth import router as auth_router
from api.routes.cinema import router as cinema_router
from api.routes.hall import router as hall_router
from api.routes.health import router as health_router
from api.routes.movie import router as movie_router
from api.routes.payment import router as payment_router
from api.routes.reservation import router as reservation_router
from api.routes.screening import router as screening_router
from core.config import get_settings
from core.rate_limit import limiter
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover.
    app.state.http_client = httpx.AsyncClient(timeout=settings.http_timeout)
    yield
    await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

register_error_handlers(app)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_base_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.include_router(auth_router)
app.include_router(cinema_router)
app.include_router(hall_router)
app.include_router(movie_router)
app.include_router(screening_router)

app.include_router(reservation_router)
app.include_router(health_router)
app.include_router(payment_router)
app.include_router(assistant_router)
