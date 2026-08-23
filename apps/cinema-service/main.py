from fastapi import FastAPI
from api.routes.cinema import router as cinema_router
from api.routes.hall import router as hall_router
from api.error_handlers import register_error_handlers
from api.routes.health import router as health_router
from api.routes.movie import router as movie_router


app = FastAPI()

register_error_handlers(app)
app.include_router(cinema_router)
app.include_router(health_router)
app.include_router(hall_router)
app.include_router(movie_router)
