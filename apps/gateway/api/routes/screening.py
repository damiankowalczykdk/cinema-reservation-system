from fastapi import APIRouter, status
from api.dependencies import CinemaServiceClientDep, admin
from domain.schemas.screening import ScreeningRead, CreateScreening, UpdateScreening

router = APIRouter(prefix="/screenings", tags=["screenings"])

@router.post("/", response_model=ScreeningRead, status_code=status.HTTP_201_CREATED, summary="Create a new screening", dependencies=[admin])
async def create_screening(payload: CreateScreening, screening_client: CinemaServiceClientDep) -> ScreeningRead:
    return await screening_client.request("POST", f"/screening/", json=payload.model_dump(mode="json"))

@router.get("/{screening_id}", response_model=ScreeningRead, status_code=status.HTTP_200_OK, summary="Get screening", dependencies=[admin])
async def get_screening_by_id(screening_id: int, screening_client: CinemaServiceClientDep) -> ScreeningRead:
    return await screening_client.request("GET", f"/screening/{screening_id}")

@router.patch("/{screening_id}", response_model=ScreeningRead, status_code=status.HTTP_200_OK, summary="Update screening", dependencies=[admin])
async def update_screening(screening_id: int, payload: UpdateScreening, screening_client: CinemaServiceClientDep) -> ScreeningRead:
    return await screening_client.request("PATCH", f"/screening/{screening_id}", json=payload.model_dump(mode="json"))

@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete screening", dependencies=[admin])
async def delete_screening_by_id(screening_id: int, screening_client: CinemaServiceClientDep) -> None:
    await screening_client.request("DELETE", f"/screening/{screening_id}")

