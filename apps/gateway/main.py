import httpx
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from routes.auth import router as auth_router
from services.cinema_client import get_cinema_health

app = FastAPI()

@app.get("/health")
async def get_health():
    async with httpx.AsyncClient() as client:
        cinema_status = await get_cinema_health(client, settings)
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