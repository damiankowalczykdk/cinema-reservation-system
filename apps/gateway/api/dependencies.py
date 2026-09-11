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

def get_client_client(client: HttpClient, settings: AuthSettings) -> ServiceRequestClient:
    return ServiceRequestClient(client, settings.cinema_service_url)

CinemaServiceClient = Annotated[ServiceRequestClient, Depends(get_client_client)]

CurrentUser = Annotated[TokenPayload, Depends(require_current_user)]

# ROLES

admin = Depends(require_roles("admin"))
user = Depends(require_roles("user"))