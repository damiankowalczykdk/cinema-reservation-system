from fastapi import APIRouter, status, Depends, HTTPException
from api.dependencies import PaymentServiceClient, CinemaServiceClient
from core.security import get_current_user
from domain.schemas.auth import TokenPayload
from domain.schemas.payment import CheckoutSessionRead, CreatePayment
from domain.schemas.reservation import ReservationRead, Status
from pydantic import TypeAdapter

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("", response_model=CheckoutSessionRead, status_code=status.HTTP_201_CREATED, summary="Create payment")
async def create_payment(
        payload: CreatePayment,
        payment_client: PaymentServiceClient,
        reservation_client: CinemaServiceClient,
        current_user: TokenPayload | None = Depends(get_current_user)
) -> CheckoutSessionRead:

    reservations = TypeAdapter(list[ReservationRead]).validate_python(await reservation_client.request(
        "GET",
        f"/reservation/{payload.group_id}"
    ))
    reservation = reservations[0]

    if reservation.user_id is not None:
        if current_user is None or reservation.user_id != current_user.sub:
            raise HTTPException(status_code=403)

    if reservation.user_id is None:
        if payload.guest_email is None or reservation.guest_email is None:
            raise HTTPException(status_code=403)

        if reservation.guest_email.lower() != payload.guest_email.lower():
            raise HTTPException(status_code=403)


    if reservation.status != Status.PENDING:
        raise HTTPException(status_code=404, detail="Reservation is not pending")


    return await payment_client.request(
        "POST",
        f"/payment",
        json={
             "group_id": reservation.group_id,
             "guest_email": payload.guest_email
        },
        headers={"X-User-Id": current_user.sub} if current_user else None
    )


