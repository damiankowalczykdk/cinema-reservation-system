import httpx
from typing import Annotated
from fastapi import Depends, Request
from core.config import Auth0Settings, get_settings
from core.http_client import ServiceRequestClient
from core.security import require_current_user
from domain.schemas.auth import TokenPayload
from api.permissions import require_roles

# AUTH

AuthSettings = Annotated[Auth0Settings, Depends(get_settings)]

def get_httpx_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

HttpClient = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]


# CINEMA-SERVICE

def get_cinema_client(client: HttpClient, settings: AuthSettings) -> ServiceRequestClient:
    return ServiceRequestClient(client, settings.cinema_service_url)

CinemaServiceClient = Annotated[ServiceRequestClient, Depends(get_cinema_client)]

# PAYMENT-SERVICE

def get_payment_client(client: HttpClient, settings: AuthSettings) -> ServiceRequestClient:
    return ServiceRequestClient(client, settings.payment_service_url)

PaymentServiceClient = Annotated[ServiceRequestClient, Depends(get_payment_client)]

# ROLES

CurrentUser = Annotated[TokenPayload, Depends(require_current_user)]

admin = Depends(require_roles("admin"))
user = Depends(require_roles("user"))