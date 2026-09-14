from pydantic import BaseModel


class CreatePayment(BaseModel):
    reservation_id: int
    amount: int
    currency: str

class CheckoutSessionRead(BaseModel):
    checkout_url: str | None