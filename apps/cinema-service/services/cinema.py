from typing import Sequence

from core.exceptions import ConflictException, NotFoundException
from domain.models.cinema import Cinema
from domain.schemas.cinema import CreateCinema, UpdateCinema
from repositories.cinema import CinemaRepository


class CinemaService:
    def __init__(self, repository: CinemaRepository):
        self.repository = repository

    async def create_cinema(self, create_cinema: CreateCinema) -> Cinema:

        if await self.repository.get_by_address(create_cinema.address):
            raise ConflictException("Cinema already exists")

        cinema = Cinema(
            name=create_cinema.name,
            city=create_cinema.city,
            address=create_cinema.address
        )

        return await self.repository.add(cinema)


    async def get_cinema_by_id(self, cinema_id: int) -> Cinema:

        cinema = await self.repository.get_by_id(cinema_id)
        if not cinema:
            raise NotFoundException("Cinema does not exist")
        return cinema

    async def get_cinema_by_name(self, name: str) -> Sequence[Cinema]:

        cinemas = await self.repository.get_by_name(name)
        if not cinemas:
            raise NotFoundException("Cinema does not exist")
        return cinemas

    async def update_cinema(self,cinema_id: int,  update_cinema: UpdateCinema) -> Cinema:

        cinema = await self.repository.get_by_id(cinema_id)
        if not cinema:
            raise NotFoundException("Cinema does not exist")

        existing_cinema = await self.repository.get_by_address(update_cinema.address)
        if existing_cinema and existing_cinema.id != cinema_id:
            raise ConflictException("Cinema already exists")

        cinema.update(update_data={
            "name": update_cinema.name,
            "city": update_cinema.city,
            "address": update_cinema.address
        })

        return await self.repository.add(cinema)

    async def delete_cinema_by_id(self, cinema_id: int) -> None:
        cinema = await self.repository.get_by_id(cinema_id)
        if not cinema:
            raise NotFoundException("Cinema does not exist")
        await self.repository.delete_by_id(cinema_id)















