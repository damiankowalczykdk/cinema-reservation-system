from typing import Mapping, Sequence, TypedDict
import httpx
from httpx import QueryParams

ParamsType = QueryParams | Mapping[str, str | int | float | bool | None | Sequence[str | int | float | bool | None]] | list[tuple[str, str | int | float | bool | None]] | tuple[tuple[str, str | int | float | bool | None], ...] | str | bytes | None

class TMDBResult(TypedDict, total=False):
    id: int
    poster_path: str | None
    site: str
    type: str
    key: str

class TMDBClient:
    def __init__(self, client: httpx.AsyncClient, tmdb_api_token: str, tmdb_base_address: str) -> None:
        self.client = client
        self.tmdb_api_token = tmdb_api_token
        self.tmdb_base_address = tmdb_base_address


    async def get_poster_path(self, title: str, year: int) -> tuple[str | None, int | None]:
        params: ParamsType = {"query": title, "year": year}
        response = await self._fetch_request(method="GET", url=f"{self.tmdb_base_address}/search/movie", params=params)

        if not response:
            return None, None

        return response[0]["poster_path"], response[0]["id"]


    async def get_trailer_key(self, tmdb_id: int) -> str | None:
        response = await self._fetch_request("GET", f"{self.tmdb_base_address}/movie/{tmdb_id}/videos")

        for r in response:
            if r["site"] == "YouTube" and r["type"] == "Trailer":
                return r["key"]

        for r in response:
            if r["site"] == "YouTube" and r["type"] == "Teaser":
                return r["key"]

        return None

    async def _fetch_request(self, method: str, url: str, params: ParamsType | None = None) -> list[TMDBResult]:
        try:
            headers = {"Authorization": f"Bearer {self.tmdb_api_token}"}
            response = await self.client.request(
                f"{method}",
                f"{url}", params=params, headers=headers
            )

        except httpx.RequestError:
            return []

        if response.status_code >= 400:
            return []

        result = response.json()
        list_result = result.get("results", [])

        return list_result










