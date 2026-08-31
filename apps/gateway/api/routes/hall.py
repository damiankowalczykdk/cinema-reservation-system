from fastapi import APIRouter, status
from api.dependencies import CinemaServiceClientDep, admin
from domain.schemas.hall import HallRead, CreateHall, UpdateHall

router = APIRouter(prefix="/halls", tags=["halls"])

@router.post("/", response_model=HallRead, status_code=status.HTTP_201_CREATED, summary="Create Hall", dependencies=[admin])
async def create_hall(payload: CreateHall, hall_client: CinemaServiceClientDep) -> HallRead:
    return await hall_client.safe_request("POST", "/hall/", json=payload.model_dump())

@router.get("/{hall_id}", response_model=HallRead, status_code=status.HTTP_200_OK, summary="Hall", dependencies=[admin])
async def get_hall_by_id(hall_id: int, hall_client: CinemaServiceClientDep) -> HallRead:
    return await hall_client.safe_request("GET", f"/hall/{hall_id}")

@router.get("/", response_model=HallRead, status_code=status.HTTP_200_OK, summary="Hall", dependencies=[admin])
async def get_hall_by_name(cinema_id: int, name: str, hall_client: CinemaServiceClientDep) -> HallRead:
    return await hall_client.safe_request("GET", "/hall/", params={"cinema_id": cinema_id, "name": name})

@router.patch("/{hall_id}", response_model=HallRead, status_code=status.HTTP_200_OK, summary="Update Hall", dependencies=[admin])
async def update_hall(hall_id: int, payload: UpdateHall, hall_client: CinemaServiceClientDep) -> HallRead:
    return await hall_client.safe_request("PATCH", f"/hall/{hall_id}", json=payload.model_dump())

@router.delete("/{hall_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Hall", dependencies=[admin])
async def delete_hall_by_id(hall_id: int, hall_client: CinemaServiceClientDep) -> None:
    await hall_client.request("DELETE", f"/hall/{hall_id}")
