from fastapi import FastAPI
from api.routes.cinema import router as cinema_router
from api.routes.health import router as health_router


app = FastAPI()

app.include_router(cinema_router)
app.include_router(health_router)
