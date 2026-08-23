from typing import Sequence
from fastapi import APIRouter, status
from api.dependencies import MovieServiceDep
from domain.models.movie import Movie
from domain.schemas.movie import MovieRead, CreateMovie, UpdateMovie

router = APIRouter(prefix="/movie", tags=["movie"])

@router.post("/", response_model=MovieRead, status_code=status.HTTP_201_CREATED, summary="Create Movie")
async def create_movie(payload: CreateMovie, service: MovieServiceDep) -> Movie:
    return await service.create_movie(payload)

@router.get("/{movie_id}", response_model=MovieRead, status_code=status.HTTP_200_OK ,summary="Get Movie")
async def get_movie_by_id(movie_id: int, service: MovieServiceDep) -> Movie:
    return await service.get_movie_by_id(movie_id)

@router.get("/", response_model=list[MovieRead], status_code=status.HTTP_200_OK, summary="Get Movies")
async def get_movie_by_title(title: str, service: MovieServiceDep) -> Sequence[Movie]:
    return await service.get_movie_by_title(title)


@router.patch("/{movie_id}", response_model=MovieRead, status_code=status.HTTP_200_OK, summary="Update Movie")
async def update_movie(movie_id: int, payload: UpdateMovie, service: MovieServiceDep) -> Movie:
    return await service.update_movie(movie_id, payload)

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Movie")
async def delete_movie(movie_id: int, service: MovieServiceDep) -> None:
    await service.delete_movie_by_id(movie_id)