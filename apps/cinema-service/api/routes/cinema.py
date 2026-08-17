from fastapi import APIRouter, status
from api.dependencies import CinemaServiceDep
from domain.models.cinema import Cinema
from domain.schemas.cinema import CinemaRead, CreateCinema, UpdateCinema

router = APIRouter(prefix="/cinema", tags=["Cinema"])


@router.post("/", response_model=CinemaRead, status_code=status.HTTP_201_CREATED, summary="Create Cinema" )
async def create_cinema(payload: CreateCinema, service: CinemaServiceDep) -> Cinema:
    return await service.create_cinema(payload)

@router.get("/{cinema_id}", response_model=CinemaRead, status_code=status.HTTP_200_OK, summary="Cinema")
async def get_cinema_by_id(cinema_id: int, service: CinemaServiceDep) -> Cinema:
    return await service.get_cinema_by_id(cinema_id)


@router.get("/", response_model=CinemaRead, status_code=status.HTTP_200_OK, summary="Cinema")
async def get_cinema_by_name(name: str, service: CinemaServiceDep) -> Cinema:
    return await service.get_cinema_by_name(name)

@router.patch("/{cinema_id}")
async def update_cinema(cinema_id: int, payload: UpdateCinema, service: CinemaServiceDep) -> Cinema:
    return await service.update_cinema(cinema_id, payload)

@router.delete("/{cinema_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Cinema")
async def delete_cinema_by_id(cinema_id: int, service: CinemaServiceDep) -> None:
    await service.delete_cinema_by_id(cinema_id)







