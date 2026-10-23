from typing import Annotated

import httpx
from core.config import Settings, settings
from core.http_client import ServiceRequestClient
from fastapi import Depends, Header, Request
from openai import AsyncOpenAI
from redis.asyncio import Redis
from repository.conversation import ConversationRepository
from service.assistant import AssistantService


def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis_client


RedisClient = Annotated[Redis, Depends(get_redis_client)]


def get_conversation_repository(redis_client: RedisClient) -> ConversationRepository:
    return ConversationRepository(redis_client)


ConversationRepo = Annotated[
    ConversationRepository, Depends(get_conversation_repository)
]


def get_httpx_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


HttpClient = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]


def get_openai_client(request: Request) -> AsyncOpenAI:
    return request.app.state.openai_client


OpenAIClient = Annotated[AsyncOpenAI, Depends(get_openai_client)]


def get_settings() -> Settings:
    return settings


AppSettings = Annotated[Settings, Depends(get_settings)]


def get_cinema_client(
    client: HttpClient, settings: AppSettings
) -> ServiceRequestClient:
    return ServiceRequestClient(client, settings.cinema_service_url)


AIClient = Annotated[ServiceRequestClient, Depends(get_cinema_client)]


def get_ai_service(cinema_client: AIClient) -> AssistantService:
    return AssistantService(cinema_client=cinema_client)


Service = Annotated[AssistantService, Depends(get_ai_service)]

User = Annotated[str | None, Header(alias="X-User-Id")]

UserEmail = Annotated[str | None, Header(alias="X-User-Email")]
