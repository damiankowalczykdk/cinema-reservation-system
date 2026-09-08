from pydantic import BaseModel, Field, ConfigDict


class LoginUrlResponse(BaseModel):
    url: str

class TokenPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sub: str
    email: str | None = None
    email_verified: bool | None = None
    permissions: list[str] = []
    scope: str = ""
    org_id: str | None = None
    roles: list[str] = Field(default=[], alias="my-namespace/globalRoles")
    