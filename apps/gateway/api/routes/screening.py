from typing import Annotated

from fastapi import APIRouter, status, Depends
from api.dependencies import CinemaServiceClient, admin
from domain.schemas.screening import ScreeningRead, CreateScreening, UpdateScreening, SearchScreeningRead, \
    SearchScreening

router = APIRouter(prefix="/screenings", tags=["screenings"])

@router.post("/", response_model=ScreeningRead, status_code=status.HTTP_201_CREATED, summary="Create a new screening", dependencies=[admin])
async def create_screening(payload: CreateScreening, screening_client: CinemaServiceClient) -> ScreeningRead:
    return await screening_client.request("POST", f"/screening/", json=payload.model_dump(mode="json"))

@router.get("/search", response_model=list[SearchScreeningRead], status_code=status.HTTP_200_OK, summary="Search screening")
async def search_screenings(payload: Annotated[SearchScreening, Depends()], screening_client: CinemaServiceClient) -> list[SearchScreeningRead]:
    return await screening_client.request("GET", f"/screening/search", params=payload.model_dump(mode="json", exclude_none=True))

@router.get("/{screening_id}", response_model=ScreeningRead, status_code=status.HTTP_200_OK, summary="Get screening")
async def get_screening_by_id(screening_id: int, screening_client: CinemaServiceClient) -> ScreeningRead:
    return await screening_client.request("GET", f"/screening/{screening_id}")

@router.patch("/{screening_id}", response_model=ScreeningRead, status_code=status.HTTP_200_OK, summary="Update screening", dependencies=[admin])
async def update_screening(screening_id: int, payload: UpdateScreening, screening_client: CinemaServiceClient) -> ScreeningRead:
    return await screening_client.request("PATCH", f"/screening/{screening_id}", json=payload.model_dump(mode="json"))

@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete screening", dependencies=[admin])
async def delete_screening_by_id(screening_id: int, screening_client: CinemaServiceClient) -> None:
    await screening_client.request("DELETE", f"/screening/{screening_id}")

