from fastapi import APIRouter, status
from api.dependencies import HallServiceDep
from domain.models.hall import Hall
from domain.schemas.hall import HallRead, CreateHall, UpdateHall

router = APIRouter(prefix="/hall", tags=["hall"])

@router.post("/", response_model=HallRead, status_code=status.HTTP_201_CREATED, summary="Create Hall" )
async def create_hall(payload: CreateHall, service: HallServiceDep) -> Hall:
    return await service.create_hall(payload)

@router.get("/{hall_id}", response_model=HallRead, status_code=status.HTTP_200_OK, summary="Hall")
async def get_hall_by_id(hall_id: int, service: HallServiceDep) -> Hall:
    return await service.get_hall_by_id(hall_id)

@router.get("/", response_model=HallRead, status_code=status.HTTP_200_OK, summary="Hall")
async def get_hall_by_name(cinema_id: int, name: str, service: HallServiceDep) -> Hall:
    return await service.get_hall_by_name(cinema_id, name)

@router.patch("/{hall_id}", response_model=HallRead, status_code=status.HTTP_200_OK, summary="Update Hall")
async def update_hall(hall_id: int, payload: UpdateHall, service: HallServiceDep) -> Hall:
    return await service.update_hall(hall_id, payload)

@router.delete("/{hall_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Hall")
async def delete_hall_by_id(hall_id: int, service: HallServiceDep) -> None:
    await service.delete_hall_by_id(hall_id)


