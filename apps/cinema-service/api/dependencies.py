from typing import Annotated, AsyncIterator
from fastapi import Depends, Header
from httpx import Request, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from clients.tmdb import TMDBClient
from core.config import database_settings
from core.database import get_db
from repositories.cinema import CinemaRepository
from repositories.hall import HallRepository
from repositories.movie import MovieRepository
from repositories.reservation import ReservationRepository
from repositories.screening import ScreeningRepository
from services.cinema import CinemaService
from services.hall import HallService
from services.movie import MovieService
from services.reservation import ReservationService
from services.screening import ScreeningService


# CINEMA

def get_cinema_repository(session: AsyncSession = Depends(get_db)) -> CinemaRepository:
    return CinemaRepository(session)

CinemaRepoDep = Annotated[CinemaRepository, Depends(get_cinema_repository)]


def get_cinema_service(repository: CinemaRepoDep) -> CinemaService:
    return CinemaService(repository)

CinemaServiceDep = Annotated[CinemaService, Depends(get_cinema_service)]

# HALL

def get_hall_repository(session: AsyncSession = Depends(get_db)) -> HallRepository:
    return HallRepository(session)

HallRepoDep = Annotated[HallRepository, Depends(get_hall_repository)]

def get_hall_service(hall_repository: HallRepoDep, cinema_repository: CinemaRepoDep) -> HallService:
    return HallService(hall_repository, cinema_repository)

HallServiceDep = Annotated[HallService, Depends(get_hall_service)]

# MOVIE

async def get_tmdb_client() -> AsyncIterator[TMDBClient]:
    async with AsyncClient(timeout=5.0) as client:
        yield TMDBClient(
            client=client,
            tmdb_api_token=database_settings.tmdb_api_token,
            tmdb_base_address=database_settings.tmdb_base_address
        )
TMDBClientDep = Annotated[TMDBClient, Depends(get_tmdb_client)]

def get_movie_repository(session: AsyncSession = Depends(get_db)) -> MovieRepository:
    return MovieRepository(session)

MovieRepoDep = Annotated[MovieRepository, Depends(get_movie_repository)]

def get_movie_service(movie_repository: MovieRepoDep, tmdb_client: TMDBClientDep) -> MovieService:
    return MovieService(movie_repository, tmdb_client)

MovieServiceDep = Annotated[MovieService, Depends(get_movie_service)]

# SCREENING

def get_screening_repository(session: AsyncSession = Depends(get_db)) -> ScreeningRepository:
    return ScreeningRepository(session)

ScreeningRepoDep = Annotated[ScreeningRepository, Depends(get_screening_repository)]

def get_screening_service(
        screening_repository: ScreeningRepoDep,
        movie_repository: MovieRepoDep,
        hall_repository: HallRepoDep,
        cinema_repository: CinemaRepoDep
) -> ScreeningService:
    return ScreeningService(screening_repository, movie_repository, hall_repository, cinema_repository)

ScreeningServiceDep = Annotated[ScreeningService, Depends(get_screening_service)]

# RESERVATION

def get_reservation_repository(session: AsyncSession = Depends(get_db)) -> ReservationRepository:
    return ReservationRepository(session)

ReservationRepoDep = Annotated[ReservationRepository, Depends(get_reservation_repository)]

def get_reservation_service(
        reservation_repository: ReservationRepoDep,
        hall_repository: HallRepoDep,
        screening_repository: ScreeningRepoDep
) -> ReservationService:
    return ReservationService(reservation_repository, hall_repository, screening_repository)

ReservationServiceDep = Annotated[ReservationService, Depends(get_reservation_service)]


# AUTH

def get_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str | None:
    return x_user_id

CurrentUserId = Annotated[str | None, Depends(get_user_id)]

def get_is_admin(is_admin: bool = Header(default=False, alias="X-Is-Admin")) -> bool:
    return is_admin

IsAdmin = Annotated[bool, Depends(get_is_admin)]

