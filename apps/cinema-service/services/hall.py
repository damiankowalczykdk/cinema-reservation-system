from core.exceptions import ConflictException, NotFoundException
from domain.models.hall import Hall
from domain.schemas.hall import CreateHall, UpdateHall
from repositories.cinema import CinemaRepository
from repositories.hall import HallRepository


class HallService:
    def __init__(self, hall_repository: HallRepository, cinema_repository: CinemaRepository):
        self.hall_repository = hall_repository
        self.cinema_repository = cinema_repository


    async def create_hall(self, create_hall: CreateHall) -> Hall:

        if not await self.cinema_repository.get_by_id(create_hall.cinema_id):
            raise NotFoundException("Cinema does not exist")


        if await self.hall_repository.get_by_cinema_id_and_hall_name(create_hall.cinema_id, create_hall.name):
            raise ConflictException("Hall already exists in this cinema")

        hall = Hall(
            cinema_id=create_hall.cinema_id,
            name=create_hall.name,
            rows=create_hall.rows,
            seats_per_row=create_hall.seats_per_row
        )

        return await self.hall_repository.add(hall)


    async def get_hall_by_id(self, hall_id: int) -> Hall:

        hall = await self.hall_repository.get_by_id(hall_id)
        if not hall:
            raise NotFoundException("Hall does not exist")
        return hall

    async def get_hall_by_name(self, cinema_id: int, name: str) -> Hall:

        hall = await self.hall_repository.get_by_cinema_id_and_hall_name(cinema_id, name)
        if not hall:
            raise NotFoundException("Hall does not exist")
        return hall

    async def update_hall(self, hall_id: int, update_hall: UpdateHall) -> Hall:

        hall = await self.hall_repository.get_by_id(hall_id)
        if not hall:
            raise NotFoundException("Hall does not exist")

        name = update_hall.name if update_hall.name is not None else hall.name

        existing_hall = await self.hall_repository.get_by_cinema_id_and_hall_name(hall.cinema_id, name)
        if existing_hall and existing_hall.id != hall.id:
            raise ConflictException("Hall already exists in this cinema")

        hall.update(update_data={
            "name": update_hall.name,
            "rows": update_hall.rows,
            "seats_per_row": update_hall.seats_per_row,
        })

        return await self.hall_repository.add(hall)

    async def delete_hall_by_id(self, hall_id: int) -> None:
        hall = await self.hall_repository.get_by_id(hall_id)
        if not hall:
            raise NotFoundException("Hall does not exist")
        await self.hall_repository.delete_by_id(hall_id)


