from fastapi import APIRouter, status, Depends
from api.dependencies import PaymentServiceClient
from core.security import get_current_user
from domain.schemas.auth import TokenPayload
from domain.schemas.payment import CheckoutSessionRead, CreatePayment

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("", response_model=CheckoutSessionRead, status_code=status.HTTP_201_CREATED, summary="Create payment")
async def create_payment(
        payload: CreatePayment,
        payment_client: PaymentServiceClient,
        current_user: TokenPayload | None = Depends(get_current_user)
) -> CheckoutSessionRead:

    return await payment_client.request(
        "POST",
        f"/payment",
        json=payload.model_dump(mode="json"),
        headers={"X-User-Id": current_user.sub} if current_user else None
    )


