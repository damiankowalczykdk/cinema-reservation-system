from typing import Callable, Annotated
from fastapi import HTTPException, status, Depends
from core.security import get_current_user
from domain.schemas.auth import TokenPayload


def require_roles(*roles: str) -> Callable:
    async def role_checker(current_user: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
        if not set(current_user.roles) & set(roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role in {', '.join(roles)}",
            )
        return current_user
    return role_checker