from pydantic import BaseModel, ConfigDict, Field


class LoginUrlResponse(BaseModel):
    url: str


class TokenPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    sub: str
    email: str | None = Field(default=None, alias="my-namespace/email")
    email_verified: bool | None = None
    permissions: list[str] = []
    scope: str = ""
    org_id: str | None = None
    roles: list[str] = Field(default=[], alias="my-namespace/globalRoles")
