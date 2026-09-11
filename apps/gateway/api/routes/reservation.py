from api.dependencies import CinemaServiceClient, admin, CurrentUser
from domain.schemas.reservation import ReservationRead, CreateReservation, OccupiedSeatsRead
from fastapi import APIRouter, status

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post(
    "/",
    response_model=ReservationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reservation"
)
async def create_reservation(
        payload: CreateReservation,
        reservation_client: CinemaServiceClient,
        current_user: CurrentUser
) -> ReservationRead:

    return await reservation_client.request(
        "POST",
        f"/reservation/",
        json=payload.model_dump(mode="json"),
        headers={"X-User-Id": current_user.sub} if current_user else None
    )
@router.get(
    "/{reservation_id}",
    response_model=ReservationRead,
    status_code=status.HTTP_200_OK,
    summary="Get reservation",
    dependencies=[admin]
)
async def get_reservation_by_id(reservation_id: int, reservation_client: CinemaServiceClient) -> ReservationRead:
    return await reservation_client.request("GET", f"/reservation/{reservation_id}")

@router.get(
    "/",
    response_model=list[ReservationRead],
    status_code=status.HTTP_200_OK,
    summary="Get User Reservation"
)
async def get_user_reservations(
        current_user: CurrentUser,
        reservation_client: CinemaServiceClient
) -> list[ReservationRead]:
    return await reservation_client.request("GET", f"/reservation/", headers={"X-User-Id": current_user.sub})

@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationRead,
    status_code=status.HTTP_200_OK,
    summary="Cancel reservation"
)
async def cancel_reservation(
        reservation_id: int,
        reservation_client: CinemaServiceClient,
        current_user: CurrentUser
) -> ReservationRead:

    headers = {"X-User-Id": current_user.sub}
    if "admin" in current_user.roles:
        headers["X-Is-Admin"] = "true"

    return await reservation_client.request(
        "POST",
        f"/reservation/{reservation_id}/cancel",
        headers=headers
    )

@router.get(
    "/screening/{screening_id}/seats",
    response_model=OccupiedSeatsRead,
    status_code=status.HTTP_200_OK,
    summary="Get screening seats"
)
async def get_occupied_seats(screening_id: int, reservation_client: CinemaServiceClient) -> OccupiedSeatsRead:
    return await reservation_client.request("GET", f"/reservation/screening/{screening_id}/seats")


@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete reservation",
    dependencies=[admin]
)
async def delete_reservation_by_id(reservation_id: int, reservation_client: CinemaServiceClient) -> None:
    await reservation_client.request("DELETE", f"/reservation/{reservation_id}")