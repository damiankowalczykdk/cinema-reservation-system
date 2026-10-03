from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from core.exceptions import ValidationException, NotFoundException, ForbiddenException, UnauthorizedException, \
    APIException
from domain.schemas.payment import CreatePayment
from main import app


def test_validation_exception_defaults() -> None:
    exc = ValidationException()

    assert exc.message == "Validation failed"
    assert exc.status_code == 400
    assert exc.error_code == "VALIDATION_ERROR"

def test_not_found_exception_defaults() -> None:
    exc = NotFoundException()

    assert exc.message == "Resource not found"
    assert exc.status_code == 404
    assert exc.error_code == "NOT_FOUND"

def test_forbidden_exception_defaults() -> None:
    exc = ForbiddenException()

    assert exc.message == "Forbidden"
    assert exc.status_code == 403
    assert exc.error_code == "FORBIDDEN"

def test_unauthorized_exception_defaults() -> None:
    exc = UnauthorizedException()

    assert exc.message == "Authentication required"
    assert exc.status_code == 401
    assert exc.error_code == "UNAUTHORIZED"

async def test_unhandled_exception_handler(client: AsyncClient) -> None:
    transport = ASGITransport(app=app, raise_app_exceptions=False)

    with patch("service.payment.PaymentService.refund", side_effect=Exception("boom")):
        async with AsyncClient(transport=transport, base_url="http://test") as raw_client:
            response = await raw_client.post("/payment/1/refund")

            assert response.status_code == 500
            assert response.json()["error"] == "INTERNAL_SERVER_ERROR"

