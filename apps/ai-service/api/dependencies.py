
from typing import Annotated

import httpx
from fastapi import Depends, Request

from core.config import settings, Settings
from core.http_client import ServiceRequestClient
from service.assistant import AssistantService


def get_httpx_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

HttpClient = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]

def get_settings() -> Settings:
    return settings

AppSettings = Annotated[Settings, Depends(get_settings)]

def get_cinema_client(client: HttpClient, settings: AppSettings) -> ServiceRequestClient:
    return ServiceRequestClient(client, settings.cinema_service_url)

AIClient = Annotated[ServiceRequestClient, Depends(get_cinema_client)]


def get_ai_service(cinema_client: AIClient) -> AssistantService:
    return AssistantService(cinema_client=cinema_client)

Service = Annotated[AssistantService, Depends(get_ai_service)]