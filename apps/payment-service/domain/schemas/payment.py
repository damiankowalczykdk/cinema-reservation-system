from pydantic import BaseModel


class CreatePayment(BaseModel):
    group_id: int
    guest_email: str | None = None

class CheckoutSessionRead(BaseModel):
    checkout_url: str | None
