from domain.schemas.payment import CheckoutSessionRead, CreatePayment
from fastapi import APIRouter, Request, Response, status

from api.dependencies import CurrentUserId, Service

router = APIRouter(prefix="/payment", tags=["payments"])


@router.post(
    "",
    response_model=CheckoutSessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment",
)
async def create_payment(
    payload: CreatePayment, service: Service, user_id: CurrentUserId
) -> CheckoutSessionRead:
    return await service.create_checkout_session(payload, user_id)


@router.post(
    "/{group_id}/refund",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Refund payment",
)
async def refund(group_id: int, service: Service):
    await service.refund(group_id)


@router.post("/webhook", status_code=status.HTTP_200_OK, summary="Stripe webhook")
async def stripe_webhook(request: Request, service: Service) -> Response:
    return await service.stripe_webhook(request)
