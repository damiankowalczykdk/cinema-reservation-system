from json import JSONDecodeError
from typing import Mapping, Sequence, Any
from fastapi import HTTPException
from httpx import QueryParams
from starlette import status
import httpx


ParamsType = QueryParams | Mapping[str, str | int | float | bool | None | Sequence[str | int | float | bool | None]] | list[tuple[str, str | int | float | bool | None]] | tuple[tuple[str, str | int | float | bool | None], ...] | str | bytes | None

HeadersType = Mapping[str, str] | None

JsonType = dict[str, Any] | list[Any] | str | int | float | bool | None


class ServiceRequestClient:

    def __init__(self, client: httpx.AsyncClient, base_url: str) -> None:
        self.client = client
        self.base_url = base_url

    async def request[T](
            self,
            method: str,
            path: str,
            *,
            json: JsonType = None,
            params: ParamsType = None,
            headers: HeadersType = None,
    ) -> T | None:

        try:
            response = await self.client.request(
                method,
                url = f"{self.base_url}{path}",
                json=json,
                params=params,
                headers=headers,
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Request failed: {str(e)}",
            )

        if response.status_code >= 400:
            error_detail: str | JsonType
            try:
                body = response.json()
                error_detail = body.get("message", body) if isinstance(body, dict) else body
            except JSONDecodeError as e:
                error_detail = str(e)
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail,
            )

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return None

        return response.json()

    async def safe_request[T](
            self,
            method: str,
            path: str,
            *,
            json: JsonType = None,
            params: ParamsType = None,
            headers: HeadersType = None,
    ) -> T:
        response: T | None = await self.request(
            method,
            path,
            json=json,
            params=params,
            headers=headers,
        )

        if response is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Upstream service returned unexpected empty response",
            )

        return response