from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from repositories.cinema import CinemaRepository
from repositories.hall import HallRepository
from services.cinema import CinemaService
from services.hall import HallService

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

def get_hall_service(hall_repository: HallRepoDep, cinema_repository: CinemaRepoDep ) -> HallService:
    return HallService(hall_repository, cinema_repository)

HallServiceDep = Annotated[HallService, Depends(get_hall_service)]






