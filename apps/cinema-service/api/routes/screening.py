from fastapi import APIRouter, status
from api.dependencies import ScreeningServiceDep
from domain.models.screening import Screening
from domain.schemas.screening import ScreeningRead, CreateScreening, UpdateScreening

router = APIRouter(prefix="/screening", tags=["screening"])

@router.post("/", response_model=ScreeningRead, status_code=status.HTTP_201_CREATED, summary="Create a new screening")
async def create_screening(payload: CreateScreening, service: ScreeningServiceDep) -> Screening:
    return await service.create_screening(payload)

@router.get("/{screening_id}", response_model=ScreeningRead, status_code=status.HTTP_200_OK, summary="Get screening")
async def get_screening_by_id(screening_id: int, service: ScreeningServiceDep) -> Screening:
    return await service.get_screenings_by_id(screening_id)

@router.patch("/{screening_id}", response_model=ScreeningRead, status_code=status.HTTP_200_OK, summary="Update screening")
async def update_screening(screening_id: int, payload: UpdateScreening, service: ScreeningServiceDep) -> Screening:
    return await service.update_screening(screening_id, payload)

@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete screening")
async def delete_screening_by_id(screening_id: int, service: ScreeningServiceDep) -> None:
    await service.delete_screening_by_id(screening_id)

