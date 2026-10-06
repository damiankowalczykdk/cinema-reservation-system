import json
import pytest
import stripe
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError
from core.config import settings
from core.exceptions import ConflictException
from domain.model.payment import Payment, Status
from domain.schemas.payment import CreatePayment
from service.payment import PaymentService


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def payment_service(fake_cinema_client, fake_stripe_client, mock_repository):
    return PaymentService(
        repository=mock_repository,
        client=fake_stripe_client,
        cinema_client=fake_cinema_client
    )

@pytest.fixture
def payment_service_stripe_error(fake_cinema_client, fake_stripe_client_stripe_error, mock_repository):
    return PaymentService(
        repository=mock_repository,
        client=fake_stripe_client_stripe_error,
        cinema_client=fake_cinema_client
    )

@pytest.fixture
def payment_service_provider_error(fake_cinema_client, fake_stripe_client_provider_error, mock_repository):
    return PaymentService(
        repository=mock_repository,
        client=fake_stripe_client_provider_error,
        cinema_client=fake_cinema_client
    )

@pytest.fixture
def payment_service_stripe_expired(fake_cinema_client, fake_stripe_client_expired, mock_repository):
    return PaymentService(
        repository=mock_repository,
        client=fake_stripe_client_expired,
        cinema_client=fake_cinema_client
    )

@pytest.fixture
def payment_service_cinema_conflict(fake_cinema_client_conflict, fake_stripe_client, mock_repository):
    return PaymentService(
        repository=mock_repository,
        client=fake_stripe_client,
        cinema_client=fake_cinema_client_conflict
    )

@pytest.fixture
def payment_service_cinema_unavailable(fake_cinema_client_unavailable, fake_stripe_client, mock_repository):
    return PaymentService(
        repository=mock_repository,
        client=fake_stripe_client,
        cinema_client=fake_cinema_client_unavailable
    )

@pytest.fixture
def payment_service_cinema_expired_time(fake_cinema_client_expire_time, fake_stripe_client, mock_repository):
    return PaymentService(
        repository=mock_repository,
        client=fake_stripe_client,
        cinema_client=fake_cinema_client_expire_time
    )

async def test_create_check_session_if_hold_expires_at_less_stripe_session(payment_service_cinema_expired_time: PaymentService, mock_repository) -> None:
    mock_repository.get_by_active_group_id = AsyncMock(return_value=None)

    create_payment = CreatePayment(
        group_id=1
    )

    with pytest.raises(ConflictException, match="Reservation hold too short to start payment"):
        await payment_service_cinema_expired_time.create_checkout_session(create_payment, "test123user")


async def test_create_checkout_session_if_pending_return_existing_url(payment_service: PaymentService, mock_repository) -> None:

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="101"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    create_payment = CreatePayment(
        group_id=1
    )

    await payment_service.create_checkout_session(create_payment, "test123user")

    mock_repository.get_by_active_group_id.assert_called_once()

async def test_create_checkout_session_if_status_completed(payment_service: PaymentService, mock_repository) -> None:

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="101"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    create_payment = CreatePayment(
        group_id=1
    )

    with pytest.raises(ConflictException, match="Reservation already paid"):
        await payment_service.create_checkout_session(create_payment, "test123user")

async def test_create_checkout_session_if_status_refunded(payment_service: PaymentService, mock_repository) -> None:

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.REFUNDED,
        stripe_session_id="101"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    create_payment = CreatePayment(
        group_id=1
    )

    with pytest.raises(ConflictException, match="Reservation already refunded"):
        await payment_service.create_checkout_session(create_payment, "test123user")


async def test_create_checkout_session_success(payment_service: PaymentService, mock_repository) -> None:

    mock_repository.get_by_active_group_id = AsyncMock(return_value=None)

    create_payment = CreatePayment(
        group_id=1
    )

    await payment_service.create_checkout_session(create_payment, "test123user")

    mock_repository.get_by_active_group_id.assert_called_once()

async def test_create_checkout_session_if_status_failed(payment_service: PaymentService, mock_repository) -> None:

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.FAILED,
        stripe_session_id="101"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    create_payment = CreatePayment(
        group_id=1
    )

    await payment_service.create_checkout_session(create_payment, "test123user")

    mock_repository.get_by_active_group_id.assert_called_once()


async def test_create_checkout_session_if_session_expired(payment_service_stripe_expired: PaymentService, mock_repository) -> None:

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="101"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    create_payment = CreatePayment(
        group_id=1
    )

    mock_repository.update = AsyncMock(return_value=payment)

    await payment_service_stripe_expired.create_checkout_session(create_payment, "test123user")

    mock_repository.get_by_active_group_id.assert_called_once()

async def test_create_checkout_session_payment_already_in_progress(payment_service: PaymentService, mock_repository) -> None:

    mock_repository.get_by_active_group_id = AsyncMock(return_value=None)

    mock_repository.add.side_effect = IntegrityError("Boom", None, BaseException())
    create_payment = CreatePayment(
        group_id=1
    )

    with pytest.raises(ConflictException, match="Payment already in progress"):
        await payment_service.create_checkout_session(create_payment, "test123user")

async def test_create_checkout_session_payment_stripe_error(payment_service_stripe_error: PaymentService, mock_repository) -> None:

    mock_repository.get_by_active_group_id = AsyncMock(return_value=None)

    create_payment = CreatePayment(
        group_id=1
    )
    with pytest.raises(HTTPException, match="Payment provider error"):
        await payment_service_stripe_error.create_checkout_session(create_payment, "test123user")


async def test_fulfill_success(payment_service: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_stripe_session_id = AsyncMock(return_value=payment)

    await payment_service.fulfill(stripe_session_id="102", event_type="checkout.session.completed", payment_status="paid", group_id=1)

    mock_repository.update.assert_called_once()


async def test_fulfill_reservation_cancelled_refunds_payment(payment_service_cinema_conflict: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_stripe_session_id = AsyncMock(return_value=payment)

    await payment_service_cinema_conflict.fulfill(stripe_session_id="102", event_type="checkout.session.completed",
                                  payment_status="paid", group_id=1)

    assert payment.status == Status.REFUNDED
    mock_repository.update.assert_called_once()

async def test_fulfill_cinema_unavailable_payment(
        payment_service_cinema_unavailable: PaymentService, mock_repository, fake_stripe_client) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_stripe_session_id = AsyncMock(return_value=payment)

    with pytest.raises(HTTPException):
        await payment_service_cinema_unavailable.fulfill(stripe_session_id="102", event_type="checkout.session.completed",
                                  payment_status="paid", group_id=1)

    mock_repository.update.assert_not_called()
    fake_stripe_client.v1.refunds.create.assert_not_called()

async def test_fulfill_already_refunded_skips(payment_service: PaymentService, mock_repository, fake_stripe_client) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.REFUNDED,
        stripe_session_id="102"
    )

    mock_repository.get_by_stripe_session_id = AsyncMock(return_value=payment)

    await payment_service.fulfill(stripe_session_id="102", event_type="checkout.session.completed",
                                  payment_status="paid", group_id=1)


    mock_repository.update.assert_not_called()
    fake_stripe_client.v1.refunds.create.assert_not_called()



async def test_fulfill_already_completed(payment_service: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="102"
    )

    mock_repository.get_by_stripe_session_id = AsyncMock(return_value=payment)

    await payment_service.fulfill(stripe_session_id="102", event_type="checkout.session.completed", payment_status="paid", group_id=1)

    mock_repository.update.assert_not_called()

async def test_fulfill_payment_not_found(payment_service: PaymentService, mock_repository) -> None:

    mock_repository.get_by_stripe_session_id = AsyncMock(return_value=None)

    await payment_service.fulfill(stripe_session_id="102", event_type="checkout.session.completed", payment_status="paid", group_id=1)

    mock_repository.update.assert_not_called()



async def test_fulfill_session_expired(payment_service: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_stripe_session_id = AsyncMock(return_value=payment)

    await payment_service.fulfill(stripe_session_id="102", event_type="checkout.session.expired", payment_status="unpaid", group_id=1)

    mock_repository.update.assert_called_once()

    res = mock_repository.update.call_args[0][0]
    assert res.status == Status.FAILED

async def test_refund_success(payment_service: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    await payment_service.refund(1)

    mock_repository.update.assert_called_once()

async def test_refund_payment_not_found(payment_service: PaymentService, mock_repository) -> None:

    mock_repository.get_by_active_group_id = AsyncMock(return_value=None)

    await payment_service.refund(1)

    mock_repository.update.assert_not_called()

async def test_refund_already_completed(payment_service: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.FAILED,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    await payment_service.refund(1)

async def test_refund_if_status_pending(payment_service_stripe_expired: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    await payment_service_stripe_expired.refund(1)

    mock_repository.update.assert_called_once()

async def test_refund_expire_fails_session_open_raises_502(payment_service: PaymentService, mock_repository, fake_stripe_client) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)


    fake_stripe_client.v1.checkout.sessions.retrieve.return_value = MagicMock(status="open", payment_intent="p1_123")
    fake_stripe_client.v1.checkout.sessions.expire.side_effect = stripe.StripeError()

    with pytest.raises(HTTPException):
        await payment_service.refund(1)

    assert payment.status == Status.PENDING

async def test_refund_expire_fails_session_complete_refunds(payment_service: PaymentService, mock_repository, fake_stripe_client) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)


    fake_stripe_client.v1.checkout.sessions.retrieve.return_value = MagicMock(status="complete", payment_intent="p1_123")
    fake_stripe_client.v1.checkout.sessions.expire.side_effect = stripe.StripeError()


    await payment_service.refund(1)

    assert payment.status == Status.REFUNDED


async def test_refund_expire_fails_session_expired_sets_failed(payment_service: PaymentService, mock_repository, fake_stripe_client) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)


    fake_stripe_client.v1.checkout.sessions.retrieve.return_value = MagicMock(status="expired")
    fake_stripe_client.v1.checkout.sessions.expire.side_effect = stripe.StripeError()

    await payment_service.refund(1)

    assert payment.status == Status.FAILED

async def test_refund_expire_fails_retrieve_fails_502(payment_service: PaymentService, mock_repository, fake_stripe_client) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.PENDING,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)


    fake_stripe_client.v1.checkout.sessions.retrieve.side_effect = stripe.StripeError()
    fake_stripe_client.v1.checkout.sessions.expire.side_effect = stripe.StripeError()

    with pytest.raises(HTTPException):
        await payment_service.refund(1)






async def test_refund_payment_intent_not_str(payment_service_provider_error: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)

    with pytest.raises(HTTPException, match="Payment provider error"):
        await payment_service_provider_error.refund(1)

async def test_refund_payment_stripe_error(payment_service_stripe_error: PaymentService, mock_repository) -> None:
    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="102"
    )

    mock_repository.get_by_active_group_id = AsyncMock(return_value=payment)


    with pytest.raises(HTTPException, match="Payment provider error"):
        await payment_service_stripe_error.refund(1)


async def test_stripe_webhook_success(payment_service: PaymentService) -> None:
    payload = json.dumps({
        "id": "evt_test_123",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_123",
                "payment_status": "paid",
                "metadata": {"group_id": "1"}
            }
        }
    })

    signature = stripe.WebhookSignature.generate_signature_header(payload, settings.stripe_webhook_secret)

    request = MagicMock()
    request.body = AsyncMock(return_value=payload.encode("utf-8"))
    request.headers = {"Stripe-Signature": signature}

    response = await payment_service.stripe_webhook(request)

    assert response.status_code == 200


async def test_stripe_webhook_invalid_signature(payment_service: PaymentService, mock_repository) -> None:
    payload = json.dumps({
        "id": "evt_test_123",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_123",
                "payment_status": "paid",
                "metadata": {"group_id": "1"}
            }
        }
    })

    request = MagicMock()
    request.body = AsyncMock(return_value=payload.encode("utf-8"))
    request.headers = {"Stripe-Signature": "bad_signature"}

    with pytest.raises(HTTPException):
        await payment_service.stripe_webhook(request)


async def test_stripe_webhook_invalid_payload(payment_service: PaymentService, mock_repository) -> None:
    payload = "bad_payload"

    signature = stripe.WebhookSignature.generate_signature_header(payload, settings.stripe_webhook_secret)

    request = MagicMock()
    request.body = AsyncMock(return_value=payload.encode("utf-8"))
    request.headers = {"Stripe-Signature": signature}

    with pytest.raises(HTTPException):
        await payment_service.stripe_webhook(request)


