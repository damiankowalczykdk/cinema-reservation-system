import json

import stripe
from httpx import AsyncClient

from core.config import settings


async def test_create_payment(client: AsyncClient) -> None:
    payload = {
        "group_id": 1,
        "guest_email": "test@example.com"
    }

    response = await client.post("/payment", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["checkout_url"] == "https://checkout.stripe.com/test"


async def test_create_payment_already_paid(client: AsyncClient) -> None:
    payload = {
        "group_id": 1,
        "guest_email": "test@example.com"
    }

    _ = await client.post("/payment", json=payload)

    webhook_payload = json.dumps({
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

    signature = stripe.WebhookSignature.generate_signature_header(webhook_payload, settings.stripe_webhook_secret)

    _ = await client.post("/payment/webhook", content=webhook_payload.encode("utf-8"),
                                 headers={"Stripe-Signature": signature})

    payload_already_paid = {
        "group_id": 1,
        "guest_email": "test@example.com"
    }

    resp = await client.post("/payment", json=payload_already_paid)
    data = resp.json()

    assert resp.status_code == 409
    assert data["error"] == "CONFLICT"
    assert data["message"] == "Reservation already paid"




async def test_create_payment_422(client: AsyncClient) -> None:
    create_payment = {
        "group_id": "bad_group_id"
    }

    response = await client.post("/payment", json=create_payment)

    assert response.status_code == 422

async def test_refund(client: AsyncClient) -> None:

    response = await client.post("/payment/1/refund")

    assert response.status_code == 204

async def test_stripe_webhook(client: AsyncClient) -> None:
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

    response = await client.post("/payment/webhook", content=payload.encode("utf-8"), headers={"Stripe-Signature": signature})

    assert response.status_code == 200