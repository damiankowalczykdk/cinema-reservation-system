from datetime import timezone, datetime
from pydantic import TypeAdapter
from api.dependencies import CinemaServiceClient, admin, CurrentUser, PaymentServiceClient
from core.security import get_current_user
from domain.schemas.auth import TokenPayload
from domain.schemas.reservation import ReservationRead, CreateReservation, OccupiedSeatsRead
from fastapi import APIRouter, status, Depends, HTTPException

from domain.schemas.screening import ScreeningRead

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post(
    "/",
    response_model=list[ReservationRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reservation"
)
async def create_reservation(
        payload: CreateReservation,
        reservation_client: CinemaServiceClient,
        current_user: TokenPayload | None = Depends(get_current_user)
) -> list[ReservationRead]:

    return await reservation_client.request(
        "POST",
        f"/reservation/",
        json=payload.model_dump(mode="json"),
        headers={"X-User-Id": current_user.sub} if current_user else None
    )
@router.get(
    "/{group_id}",
    response_model=list[ReservationRead],
    status_code=status.HTTP_200_OK,
    summary="Get reservations",
    dependencies=[admin]
)
async def get_reservations_group_by_id(group_id: int, reservation_client: CinemaServiceClient) -> list[ReservationRead]:
    return await reservation_client.request("GET", f"/reservation/{group_id}")

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
    "/{group_id}/cancel",
    response_model=list[ReservationRead],
    status_code=status.HTTP_200_OK,
    summary="Cancel reservation"
)
async def cancel_reservation(
        group_id: int,
        reservation_client: CinemaServiceClient,
        payment_client: PaymentServiceClient,
        current_user: CurrentUser
) -> list[ReservationRead]:

    reservations = TypeAdapter(list[ReservationRead]).validate_python(await reservation_client.request(
        "GET",
        f"/reservation/{group_id}"
    ))
    reservation = reservations[0]

    headers = {"X-User-Id": current_user.sub}
    is_admin = "admin" in current_user.roles
    if is_admin:
        headers["X-Is-Admin"] = "true"

    if not is_admin and (reservation.user_id is None or current_user.sub != reservation.user_id):
        raise HTTPException(status_code=404)

    screening_id = reservation.screening_id

    screening = ScreeningRead.model_validate(await reservation_client.request(
        "GET",
        f"/screening/{screening_id}"
    ))

    if not is_admin and screening.start_time < datetime.now(timezone.utc):
        raise HTTPException(status_code=409, detail="Cannot cancel reservation screening already started")

    await payment_client.request(
        "POST",
        f"/payment/{group_id}/refund"
    )

    return await reservation_client.request(
        "POST",
        f"/reservation/{group_id}/cancel",
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
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete reservation",
    dependencies=[admin]
)
async def delete_reservation_group(group_id: int, reservation_client: CinemaServiceClient) -> None:
    await reservation_client.request("DELETE", f"/reservation/{group_id}")