from fastapi.exceptions import HTTPException
from fastapi import Request, Response
from core.config import settings
from domain.model.payment import Payment, Status
from domain.schemas.payment import CreatePayment, CheckoutSessionRead
from repository.payment import PaymentRepository
import stripe


class PaymentService:
    def __init__(self, repository: PaymentRepository, client: stripe.StripeClient):
        self.repository = repository
        self.client = client



    async def create_checkout_session(self, create_payment: CreatePayment) -> CheckoutSessionRead:
        try:
            checkout_session = self.client.v1.checkout.sessions.create(params={
                'line_items': [
                    {
                        "price_data": {
                            "currency": create_payment.currency,
                            "product_data": {"name": f"Reservation {create_payment.reservation_id}"},
                            "unit_amount": create_payment.amount
                        },
                        "quantity": 1
                    },
                ],
                'mode': 'payment',
                'success_url': f"{settings.frontend_url}" + '/success.html',
                # Provide a name (for example, hosted_web_0001) to label this Checkout integration and measure its conversion independently
                'integration_identifier': 'cinema-reservation-checkout',
            })
            await self.repository.add(Payment(
                reservation_id=create_payment.reservation_id,
                amount=create_payment.amount,
                currency=create_payment.currency,
                status=Status.PENDING,
                stripe_session_id=checkout_session.id
            ))

        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

        return CheckoutSessionRead(checkout_url=checkout_session.url)


    async def fulfill(self, stripe_session_id: str) -> None:
        payment = await self.repository.get_by_stripe_session_id(stripe_session_id)
        if payment is None:
            return

        if payment.status == Status.COMPLETED:
            return

        checkout_session = self.client.v1.checkout.sessions.retrieve(
            stripe_session_id,
            params={'expand': ['line_items']},
        )

        if checkout_session.payment_status == "paid":
            payment.status = Status.COMPLETED

        await self.repository.update(payment)

    async def stripe_webhook(self, request: Request) -> Response:
        payload = await request.body()
        sig_header = request.headers.get("Stripe-Signature")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.stripe_webhook_secret
            )
        except ValueError as e:
            raise HTTPException(status_code=400)
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400)

        if event.type == "checkout.session.completed":
            await self.fulfill(event.data.object.id)

        return Response(status_code=200)



