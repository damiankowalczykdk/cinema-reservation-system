from typing import Sequence
from fastapi import APIRouter, status
from api.dependencies import ReservationServiceDep, CurrentUserId, IsAdmin
from domain.models.reservation import Reservation
from domain.schemas.reservation import ReservationRead, CreateReservation, OccupiedSeatsRead, GroupTotalRead, ExtendRead

router = APIRouter(prefix="/reservation", tags=["reservation"])

@router.post("/", response_model=list[ReservationRead], status_code=status.HTTP_201_CREATED, summary="Create a new reservation")
async def create_reservation(payload: CreateReservation, service: ReservationServiceDep, user_id: CurrentUserId) -> Sequence[Reservation]:
    return await service.create_reservation(payload, user_id)


@router.get("/{group_id}", response_model=list[ReservationRead], status_code=status.HTTP_200_OK, summary="Get reservations")
async def get_reservations_by_group_id(group_id: int, service: ReservationServiceDep) -> Sequence[Reservation]:
    return await service.get_reservations_by_group_id(group_id)

@router.post("/{group_id}/extend",response_model=ExtendRead, status_code=status.HTTP_200_OK, summary="Extend reservations")
async def extend(group_id: int, service: ReservationServiceDep) -> ExtendRead:
    return ExtendRead(expires_at=await service.extend(group_id))

@router.post("/expire-stale", status_code=status.HTTP_204_NO_CONTENT, summary="Expire stale reservations")
async def expire_stale(service: ReservationServiceDep) -> None:
    await service.expire_stale()


@router.get("/{group_id}/total",response_model=GroupTotalRead, status_code=status.HTTP_200_OK, summary="Get reservations total")
async def get_group_total(group_id: int, service: ReservationServiceDep) -> GroupTotalRead:
    return GroupTotalRead(total_price=await service.get_group_total(group_id))


@router.get("/", response_model=list[ReservationRead], status_code=status.HTTP_200_OK, summary="Get User Reservation")
async def get_user_reservations(user_id: CurrentUserId, service: ReservationServiceDep) -> Sequence[Reservation]:
    return await service.get_user_reservations(user_id)

@router.post("/{group_id}/cancel", response_model=list[ReservationRead], status_code=status.HTTP_200_OK, summary="Cancel reservation")
async def cancel_reservation(group_id: int, service: ReservationServiceDep, user_id: CurrentUserId, is_admin: IsAdmin) -> Sequence[Reservation]:
    return await service.cancel_reservation(group_id, user_id, is_admin)

@router.get("/screening/{screening_id}/seats", response_model=OccupiedSeatsRead, status_code=status.HTTP_200_OK, summary="Get occupied seats")
async def get_occupied_seats(screening_id: int, service: ReservationServiceDep) -> OccupiedSeatsRead:
    return await service.get_occupied_seats(screening_id)

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete reservation")
async def delete_reservation_group(group_id: int, service: ReservationServiceDep) -> None:
    await service.delete_reservation_group(group_id)


@router.post("/{group_id}/confirm", status_code=status.HTTP_200_OK, summary="Confirm reservation")
async def set_confirm_reservation(group_id: int, service: ReservationServiceDep) -> None:
    await service.set_confirm_reservation(group_id)

