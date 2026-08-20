from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from repositories.cinema import CinemaRepository
from services.cinema import CinemaService


def get_cinema_repository(session: AsyncSession = Depends(get_db)) -> CinemaRepository:
    return CinemaRepository(session)

CinemaRepoDep = Annotated[CinemaRepository, Depends(get_cinema_repository)]


def get_cinema_service(repository: CinemaRepoDep) -> CinemaService:
    return CinemaService(repository)

CinemaServiceDep = Annotated[CinemaService, Depends(get_cinema_service)]







