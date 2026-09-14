from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.payment import router as payment_router
from core.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment_router)
