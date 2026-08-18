from fastapi import FastAPI
from api.routes.cinema import router as cinema_router
from api.routes.error_handlers import register_error_handlers
from api.routes.health import router as health_router


app = FastAPI()

register_error_handlers(app)
app.include_router(cinema_router)
app.include_router(health_router)
