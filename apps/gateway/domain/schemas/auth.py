from pydantic import BaseModel

class LoginUrlResponse(BaseModel):
    url: str

class TokenPayload(BaseModel):
    sub: str
    email: str | None = None
    email_verified: bool | None = None
    permissions: list[str] = []
    scope: str = ""
    org_id: str | None = None
    