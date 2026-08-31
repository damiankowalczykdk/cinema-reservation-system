from typing import Sequence

from core.exceptions import ConflictException, NotFoundException
from domain.models.movie import Movie
from domain.schemas.movie import CreateMovie, UpdateMovie
from repositories.movie import MovieRepository


class MovieService:
    def __init__(self, repository: MovieRepository) -> None:
        self.repository = repository

    async def create_movie(self, create_movie: CreateMovie) -> Movie:
        if await self.repository.get_movie_by_title_and_release_date(create_movie.title, create_movie.release_date):
            raise ConflictException("Movie already exists")

        movie = Movie(
            title=create_movie.title,
            description=create_movie.description,
            duration_minutes=create_movie.duration_minutes,
            genre=create_movie.genre,
            release_date=create_movie.release_date,
        )

        return await self.repository.add(movie)

    async def get_movie_by_id(self, movie_id: int) -> Movie:
        movie = await self.repository.get_by_id(movie_id)
        if not movie:
            raise NotFoundException("Movie not found")
        return movie

    async def get_movie_by_title(self, title: str) -> Sequence[Movie]:
        movies = await self.repository.get_movie_by_title(title)
        if not movies:
            raise NotFoundException("Movie not found")
        return movies

    async def update_movie(self, movie_id: int,  update_movie: UpdateMovie) -> Movie:

        movie = await self.repository.get_by_id(movie_id)
        if not movie:
            raise NotFoundException("Movie not found")

        title = update_movie.title if update_movie.title is not None else movie.title
        release_date = update_movie.release_date if update_movie.release_date is not None else movie.release_date

        existing_movie = await self.repository.get_movie_by_title_and_release_date(title, release_date)
        if existing_movie and existing_movie.id != movie.id:
            raise ConflictException("Movie already exists")

        movie.update(update_data={
            "title": update_movie.title,
            "description": update_movie.description,
            "duration_minutes": update_movie.duration_minutes,
            "genre": update_movie.genre,
            "release_date": update_movie.release_date
        })

        return await self.repository.add(movie)

    async def delete_movie_by_id(self, movie_id: int) -> None:
        movie = await self.repository.get_by_id(movie_id)
        if not movie:
            raise NotFoundException("Movie not found")

        await self.repository.delete_by_id(movie_id)