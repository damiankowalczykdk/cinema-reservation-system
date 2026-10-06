from typing import Mapping, Sequence
import httpx
from httpx import QueryParams

ParamsType = QueryParams | Mapping[str, str | int | float | bool | None | Sequence[str | int | float | bool | None]] | list[tuple[str, str | int | float | bool | None]] | tuple[tuple[str, str | int | float | bool | None], ...] | str | bytes | None


class TMDBClient:
    def __init__(self, client: httpx.AsyncClient, tmdb_api_token: str, tmdb_base_address: str) -> None:
        self.client = client
        self.tmdb_api_token = tmdb_api_token
        self.tmdb_base_address = tmdb_base_address

    async def get_poster_path(self, title: str, year: int) -> str | None:
        try:
            params: ParamsType = {"query": title, "year": year}
            headers = {"Authorization": f"Bearer {self.tmdb_api_token}"}
            response = await self.client.request(
                "GET",
                f"{self.tmdb_base_address}/search/movie", params=params, headers=headers
            )

        except httpx.RequestError:
            return None

        if response.status_code >= 400:
            return None

        result = response.json()
        list_result = result.get("results", [])

        if not list_result:
            return None

        return list_result[0]["poster_path"]





