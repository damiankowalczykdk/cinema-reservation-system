from datetime import timedelta
from core.exceptions import NotFoundException, ConflictException
from domain.models.hall import Hall
from domain.models.movie import Movie
from domain.models.screening import Screening
from domain.schemas.screening import CreateScreening, UpdateScreening
from repositories.hall import HallRepository
from repositories.movie import MovieRepository
from repositories.screening import ScreeningRepository


class ScreeningService:
    def __init__(self,
                 screening_repository: ScreeningRepository,
                 movie_repository: MovieRepository,
                 hall_repository: HallRepository
    ) -> None:
        self.screening_repository = screening_repository
        self.movie_repository = movie_repository
        self.hall_repository = hall_repository

    async def create_screening(self, create_screening: CreateScreening) -> Screening:
        movie = await self._check_movie_by_id(create_screening.movie_id)

        await self._check_hall_by_id(create_screening.hall_id)

        end_time = create_screening.start_time + timedelta(minutes=movie.duration_minutes)

        overlapping = await self.screening_repository.get_overlapping_screenings(
                create_screening.hall_id,
                create_screening.start_time,
                end_time
        )
        if overlapping:
            raise ConflictException("Hall already has a screening at this time")

        screening = Screening(
            movie_id=create_screening.movie_id,
            hall_id=create_screening.hall_id,
            start_time=create_screening.start_time,
            price=create_screening.price,
        )

        return await self.screening_repository.add(screening)

    async def get_screenings_by_id(self, screening_id: int) -> Screening:
        screening = await self._check_screening_by_id(screening_id)
        return screening

    async def update_screening(self, screening_id: int, update_screening: UpdateScreening) -> Screening:
        screening = await self._check_screening_by_id(screening_id)

        movie_id = update_screening.movie_id if update_screening.movie_id is not None else screening.movie_id
        hall_id = update_screening.hall_id if update_screening.hall_id is not None else screening.hall_id
        start_time = update_screening.start_time if update_screening.start_time is not None else screening.start_time

        movie = await self._check_movie_by_id(movie_id)

        await self._check_hall_by_id(hall_id)

        end_time = start_time + timedelta(minutes=movie.duration_minutes)

        overlapping = await self.screening_repository.get_overlapping_screenings(hall_id, start_time, end_time)
        overlapping = [s for s in overlapping if s.id != screening_id]
        if overlapping:
            raise ConflictException("Hall already has a screening at this time")

        screening.update(update_data={
            "movie_id": update_screening.movie_id,
            "hall_id": update_screening.hall_id,
            "start_time": update_screening.start_time,
            "price": update_screening.price,
        })

        return await self.screening_repository.add(screening)


    async def delete_screening_by_id(self, screening_id: int) -> None:
        await self._check_screening_by_id(screening_id)
        await self.screening_repository.delete_by_id(screening_id)


    async def _check_screening_by_id(self, screening_id: int) -> Screening:
        screening = await self.screening_repository.get_by_id(screening_id)
        if not screening:
            raise NotFoundException("Screening not found")
        return screening

    async def _check_movie_by_id(self, movie_id: int) -> Movie:
        movie = await self.movie_repository.get_by_id(movie_id)
        if not movie:
            raise NotFoundException("Movie not found")
        return movie

    async def _check_hall_by_id(self, hall_id: int) -> Hall:
        hall = await self.hall_repository.get_by_id(hall_id)
        if not hall:
            raise NotFoundException("Hall not found")
        return hall
