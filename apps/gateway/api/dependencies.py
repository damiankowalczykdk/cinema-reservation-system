from typing import Annotated

import httpx
from fastapi import Depends, Request
from core.config import Auth0Settings, get_settings
from core.http_client import ServiceRequestClient




Auth0SettingsDep = Annotated[Auth0Settings, Depends(get_settings)]

def get_httpx_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

HttpClient = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]

def get_client_client(client: HttpClient, settings: Auth0SettingsDep) -> ServiceRequestClient:
    return ServiceRequestClient(client, settings.cinema_service_url)

CinemaServiceClientDep = Annotated[ServiceRequestClient, Depends(get_client_client)]