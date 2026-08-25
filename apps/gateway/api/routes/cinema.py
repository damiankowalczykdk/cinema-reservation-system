from fastapi import APIRouter, status
from domain.schemas.cinema import CinemaRead, CreateCinema, UpdateCinema
from api.dependencies import CinemaServiceClientDep

router = APIRouter(prefix="/cinemas", tags=["Cinemas"])

@router.post("/", response_model=CinemaRead, status_code=status.HTTP_201_CREATED, summary="Create Cinema" )
async def create_cinema(payload: CreateCinema, cinema_client: CinemaServiceClientDep) -> CinemaRead:
    return await cinema_client.safe_request("POST", "/cinema/", json=payload.model_dump())

@router.get("/{cinema_id}", response_model=CinemaRead, status_code=status.HTTP_200_OK, summary="Cinema by ID")
async def get_cinema_by_id(cinema_id: int, cinema_client: CinemaServiceClientDep) -> CinemaRead:
    return await cinema_client.safe_request("GET", f"/cinema/{cinema_id}")

@router.get("/", response_model=list[CinemaRead], status_code=status.HTTP_200_OK, summary="Cinema by name")
async def get_cinema_by_name(name: str, cinema_client: CinemaServiceClientDep) -> list[CinemaRead]:
    return await cinema_client.safe_request("GET", f"/cinema/", params={"name": name})

@router.patch("/{cinema_id}", response_model=CinemaRead, status_code=status.HTTP_200_OK, summary="Update Cinema")
async def update_cinema(cinema_id: int, payload: UpdateCinema, cinema_client: CinemaServiceClientDep) -> CinemaRead:
    return await cinema_client.safe_request("PATCH", f"/cinema/{cinema_id}", json=payload.model_dump())

@router.delete("/{cinema_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Cinema")
async def delete_cinema_by_id(cinema_id: int, cinema_client: CinemaServiceClientDep) -> None:
    await cinema_client.request("DELETE", f"/cinema/{cinema_id}")