import stripe
import logging
from fastapi import Response, Request
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from core.config import settings
from core.exceptions import ConflictException
from core.http_client import ServiceRequestClient
from domain.model.payment import Payment, Status
from domain.schemas.payment import CreatePayment, CheckoutSessionRead, ReservationRead
from repository.payment import PaymentRepository


logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(
            self,
            repository: PaymentRepository,
            client: stripe.StripeClient,
            cinema_client: ServiceRequestClient
    ) -> None:
        self.repository = repository
        self.client = client
        self.cinema_client = cinema_client



    async def create_checkout_session(self, create_payment: CreatePayment, user_id: str | None = None) -> CheckoutSessionRead:

        reservation = ReservationRead.model_validate(await  self.cinema_client.request(
            "GET",
            f"/reservation/{create_payment.reservation_id}"

        ))

        reservation_active = await self.repository.get_by_active_reservation_id(create_payment.reservation_id)

        new_active_session = reservation_active is None

        if reservation_active is not None:
            if reservation_active.status == Status.PENDING:
                checkout_active_session = self.client.v1.checkout.sessions.retrieve(
                    reservation_active.stripe_session_id)

                if checkout_active_session.status == "expired":
                    reservation_active.status = Status.FAILED
                    await self.repository.update(reservation_active)
                    new_active_session = True

                else:
                    return CheckoutSessionRead(checkout_url=checkout_active_session.url)

            elif reservation_active.status == Status.COMPLETED:
                raise ConflictException("Reservation already paid")

            elif reservation_active.status == Status.FAILED:
                new_active_session = True

            elif reservation_active.status == Status.REFUNDED:
                raise ConflictException("Reservation already refunded")

        if new_active_session:
            try:

                checkout_session = self.client.v1.checkout.sessions.create(params={
                    'line_items': [
                        {
                            "price_data": {
                                "currency": settings.default_currency,
                                "product_data": {"name": f"Reservation {create_payment.reservation_id}"},
                                "unit_amount": int(reservation.price_paid * 100)
                            },
                            "quantity": 1
                        },
                    ],
                    'mode': 'payment',
                    'success_url': f"{settings.frontend_url}/booking/confirmation?session_id={{CHECKOUT_SESSION_ID}}",
                    'metadata': {'reservation_id': str(create_payment.reservation_id)},
                    # Provide a name (for example, hosted_web_0001) to label this Checkout integration and measure its conversion independently
                    'integration_identifier': 'cinema-reservation-checkout',
                })


                await self.repository.add(Payment(
                    reservation_id=create_payment.reservation_id,
                    user_id=user_id,
                    amount=int(reservation.price_paid * 100),
                    currency=settings.default_currency,
                    status=Status.PENDING,
                    stripe_session_id=checkout_session.id
                ))
            except IntegrityError:
                raise ConflictException("Payment already in progress")

            except stripe.StripeError as e:
                logger.exception("Stripe checkout session failed")
                raise HTTPException(status_code=502, detail="Payment provider error")



        return CheckoutSessionRead(checkout_url=checkout_session.url)


    async def fulfill(self, stripe_session_id: str, event_type: str, payment_status: str, reservation_id: int) -> None:

        payment = await self.repository.get_by_stripe_session_id(stripe_session_id)

        if payment is None:
            return None

        if payment.status == Status.COMPLETED:
            return None

        if payment_status == "paid":
            payment.status = Status.COMPLETED

            await self.cinema_client.request(
                "POST",
            f"/reservation/{reservation_id}/confirm")


        if event_type in ("checkout.session.expired", "checkout.session.async_payment_failed"):
            payment.status = Status.FAILED


        await self.repository.update(payment)

        return None

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

        if event.type in ("checkout.session.completed", "checkout.session.expired", "checkout.session.async_payment_succeeded",
         "checkout.session.async_payment_failed"):
            await self.fulfill(
                event.data.object.id,
                event.type,
                event.data.object.payment_status,
                int(event.data.object.metadata.reservation_id)
            )


        return Response(status_code=200)
