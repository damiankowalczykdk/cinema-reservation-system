from typing import Sequence
from fastapi import APIRouter, status
from api.dependencies import ReservationServiceDep, CurrentUserId, IsAdmin
from domain.models.reservation import Reservation
from domain.schemas.reservation import ReservationRead, CreateReservation, OccupiedSeatsRead

router = APIRouter(prefix="/reservation", tags=["reservation"])

@router.post("/", response_model=ReservationRead, status_code=status.HTTP_201_CREATED, summary="Create a new reservation")
async def create_reservation(payload: CreateReservation, service: ReservationServiceDep, user_id: CurrentUserId) -> Reservation:
    return await service.create_reservation(payload, user_id)

@router.get("/{reservation_id}", response_model=ReservationRead, status_code=status.HTTP_200_OK, summary="Get reservation")
async def get_reservation_by_id(reservation_id: int, service: ReservationServiceDep) -> Reservation:
    return await service.get_reservation_by_id(reservation_id)

@router.get("/", response_model=list[ReservationRead], status_code=status.HTTP_200_OK, summary="Get User Reservation")
async def get_user_reservations(user_id: CurrentUserId, service: ReservationServiceDep) -> Sequence[Reservation]:
    return await service.get_user_reservations(user_id)

@router.post("/{reservation_id}/cancel", response_model=ReservationRead, status_code=status.HTTP_200_OK, summary="Cancel reservation")
async def cancel_reservation(reservation_id: int, service: ReservationServiceDep, user_id: CurrentUserId, is_admin: IsAdmin) -> Reservation:
    return await service.cancel_reservation(reservation_id, user_id, is_admin)

@router.get("/screening/{screening_id}/seats", response_model=OccupiedSeatsRead, status_code=status.HTTP_200_OK, summary="Get occupied seats")
async def get_occupied_seats(screening_id: int, service: ReservationServiceDep) -> OccupiedSeatsRead:
    return await service.get_occupied_seats(screening_id)

@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete reservation")
async def delete_reservation(reservation_id: int, service: ReservationServiceDep) -> None:
    return await service.delete_reservation_by_id(reservation_id)


