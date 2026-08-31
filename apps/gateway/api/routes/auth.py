import secrets
import urllib.parse
import httpx
from fastapi import APIRouter, Request, HTTPException, Response
from starlette.responses import RedirectResponse
from starlette.status import HTTP_502_BAD_GATEWAY

from api.dependencies import CurrentUserDep
from core.config import settings
from domain.schemas.auth import TokenPayload, LoginUrlResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login-url", response_model=LoginUrlResponse)
async def get_login_url(request: Request) -> LoginUrlResponse:

    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    params = {
        "response_type": "code",
        "client_id": settings.auth0_client_id,
        "redirect_uri": settings.auth0_callback_url,
        "scope": "openid profile email",
        "audience": settings.auth0_audience,
        "state": state
    }

    url = f"https://{settings.auth0_domain}/authorize?{urllib.parse.urlencode(params)}"
    return LoginUrlResponse(url=url)


@router.get("/callback")
async def auth_callback(request: Request, code: str, state: str):

    stored_state = request.session.pop("oauth_state", "")
    if not secrets.compare_digest(state, stored_state):
        raise HTTPException(status_code=400, detail="Invalid state - possible attacks CSRF")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            f"https://{settings.auth0_domain}/oauth/token",
            json={
                "grant_type": "authorization_code",
                "client_id": settings.auth0_client_id,
                "client_secret": settings.auth0_client_secret,
                "code": code,
                "redirect_uri": settings.auth0_callback_url,
            },
            timeout=settings.http_timeout
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=HTTP_502_BAD_GATEWAY, detail="Invalid authorization code")

        tokens = token_response.json()
        response = RedirectResponse(url=settings.app_base_url)
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=tokens.get("expires_in", 3600),
            path="/"
        )

        return response

@router.get("/me", response_model=TokenPayload)
async def get_current_user(user: CurrentUserDep) -> TokenPayload:
    return user

@router.get("/logout-url", response_model=LoginUrlResponse)
async def get_logout_url() -> LoginUrlResponse:
    params = {
        "client_id": settings.auth0_client_id,
        "returnTo": settings.app_base_url
    }
    url = f"https://{settings.auth0_domain}/v2/logout?{urllib.parse.urlencode(params)}"
    return LoginUrlResponse(url=url)


@router.post("/logout")
async def logout_user(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key="access_token",
        path="/"
    )

    return {"message": "Successfully logged out."}