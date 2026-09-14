from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from core.database import get_db
from repository.payment import PaymentRepository
from service.payment import PaymentService
from stripe import StripeClient


async def get_payment_repository(session: AsyncSession = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(session)

async def get_stripe_client() -> StripeClient:
    return StripeClient(settings.stripe_secret_key)

Client = Annotated[StripeClient, Depends(get_stripe_client)]


Repository = Annotated[PaymentRepository, Depends(get_payment_repository)]

async def get_payment_service(repository: Repository, client: Client) -> PaymentService:
    return PaymentService(repository, client)

Service = Annotated[PaymentService, Depends(get_payment_service)]






