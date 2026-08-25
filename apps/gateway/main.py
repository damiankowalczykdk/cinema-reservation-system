from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from api.error_handlers import register_error_handlers
from api.routes.auth import router as auth_router
from clients.cinema import get_cinema_health
from api.routes.cinema import router as cinema_router
from api.dependencies import CinemaClientDep
from core.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=settings.http_timeout)
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)


register_error_handlers(app)

@app.get("/health")
async def get_health(cinema_client: CinemaClientDep):
    cinema_status = await get_cinema_health(cinema_client)
    overall = "ok" if cinema_status.get("status") == "ok" else "degraded"
    return {"status": overall, "gateway": "ok", "cinema_status": cinema_status}


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_base_url],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.include_router(auth_router)
app.include_router(cinema_router)