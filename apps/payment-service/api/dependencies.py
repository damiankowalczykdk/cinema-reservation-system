from functools import lru_cache
from typing import Annotated
import httpx
from fastapi import Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import Settings
from core.database import get_db
from core.http_client import ServiceRequestClient
from repository.payment import PaymentRepository
from service.payment import PaymentService
from stripe import StripeClient

def get_httpx_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

HttpClient = Annotated[httpx.AsyncClient, Depends(get_httpx_client)]


# CINEMA-SERVICE
@lru_cache
def get_settings() -> Settings:
    return Settings() #type: ignore

AppSettings = Annotated[Settings, Depends(get_settings)]


def get_cinema_client(client: HttpClient, settings: AppSettings) -> ServiceRequestClient:
    return ServiceRequestClient(client, settings.cinema_service_url)

CinemaServiceClient = Annotated[ServiceRequestClient, Depends(get_cinema_client)]


# PAYMENT

async def get_payment_repository(session: AsyncSession = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(session)

Repository = Annotated[PaymentRepository, Depends(get_payment_repository)]

async def get_stripe_client(request: Request) -> StripeClient:
    return request.app.state.stripe_client

Client = Annotated[StripeClient, Depends(get_stripe_client)]


async def get_payment_service(repository: Repository, client: Client, cinema_client: CinemaServiceClient) -> PaymentService:
    return PaymentService(repository, client, cinema_client)

Service = Annotated[PaymentService, Depends(get_payment_service)]




def get_user_id(user_id: str | None = Header(default=None, alias="X-User-Id")) -> str | None:
    return user_id


CurrentUserId = Annotated[str | None, Depends(get_user_id)]





