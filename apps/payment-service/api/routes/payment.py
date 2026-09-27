from fastapi import APIRouter,status, Request, Response

from api.dependencies import Service, CurrentUserId
from domain.schemas.payment import CreatePayment, CheckoutSessionRead

router = APIRouter(prefix="/payment", tags=["payments"])

@router.post("", response_model=CheckoutSessionRead, status_code=status.HTTP_201_CREATED, summary=f"Create payment")
async def create_payment(payload: CreatePayment, service: Service, user_id: CurrentUserId) -> CheckoutSessionRead:
    return await service.create_checkout_session(payload, user_id)

@router.post("/{group_id}/refund", status_code=status.HTTP_204_NO_CONTENT, summary=f"Refund payment")
async def refund(group_id: int, service: Service):
    await service.refund(group_id)


@router.post("/webhook", status_code=status.HTTP_200_OK, summary=f"Stripe webhook")
async def stripe_webhook(request: Request, service: Service) -> Response:
    return await service.stripe_webhook(request)