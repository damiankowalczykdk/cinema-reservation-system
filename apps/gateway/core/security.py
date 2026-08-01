import jwt
from typing import Annotated
from fastapi import Depends, status, HTTPException, Request
from jwt import PyJWKClient, InvalidTokenError

from core.config import settings
from domain.schemas import TokenPayload

jwks_client = PyJWKClient(
    f"https://{settings.auth0_domain}/.well-known/jwks.json",
    cache_keys=True,
    lifespan=300
)

async def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return token

async def get_current_user(
        token: Annotated[str, Depends(get_token_from_cookie)]
) -> TokenPayload:

    try:
        signin_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signin_key.key,
            algorithms=["RS256"],
            audience=settings.auth0_audience,
            issuer=f"https://{settings.auth0_domain}/"
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenPayload(**payload)

CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]