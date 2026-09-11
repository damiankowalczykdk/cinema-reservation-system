import jwt
from fastapi import status, HTTPException, Request, Depends
from jwt import PyJWKClient, InvalidTokenError
from core.config import settings
from domain.schemas.auth import TokenPayload
from typing import Annotated

jwks_client = PyJWKClient(
    f"https://{settings.auth0_domain}/.well-known/jwks.json",
    cache_keys=True,
    lifespan=300
)

async def get_current_user(request: Request) -> TokenPayload | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:

        signin_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signin_key.key,
            algorithms=["RS256"],
            audience=settings.auth0_audience,
            issuer=f"https://{settings.auth0_domain}/"
    )

    except InvalidTokenError:
        return None

    return TokenPayload(**payload)

async def require_current_user(current_user: Annotated[TokenPayload, Depends(get_current_user)]):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return current_user