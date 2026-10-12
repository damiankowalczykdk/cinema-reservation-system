from typing import Mapping, Sequence
import httpx
from httpx import QueryParams

ParamsType = QueryParams | Mapping[str, str | int | float | bool | None | Sequence[str | int | float | bool | None]] | list[tuple[str, str | int | float | bool | None]] | tuple[tuple[str, str | int | float | bool | None], ...] | str | bytes | None


class TMDBClient:
    def __init__(self, client: httpx.AsyncClient, tmdb_api_token: str, tmdb_base_address: str) -> None:
        self.client = client
        self.tmdb_api_token = tmdb_api_token
        self.tmdb_base_address = tmdb_base_address

    async def get_poster_path(self, title: str, year: int) -> tuple[str | None, int | None]:
        try:
            params: ParamsType = {"query": title, "year": year}
            headers = {"Authorization": f"Bearer {self.tmdb_api_token}"}
            response = await self.client.request(
                "GET",
                f"{self.tmdb_base_address}/search/movie", params=params, headers=headers
            )

        except httpx.RequestError:
            return None, None

        if response.status_code >= 400:
            return None, None

        result = response.json()
        list_result = result.get("results", [])

        if not list_result:
            return None, None

        return list_result[0]["poster_path"], list_result[0]["id"]

    async def get_trailer_key(self, tmdb_id: int) -> str | None:
        try:
            headers = {"Authorization": f"Bearer {self.tmdb_api_token}"}

            response = await self.client.request(
                "GET",
                f"{self.tmdb_base_address}/movie/{tmdb_id}/videos",
                headers=headers,
            )
        except httpx.RequestError:
            return None

        if response.status_code >= 400:
            return None

        result = response.json()


        list_result = result.get("results", [])

        for r in list_result:
            if r["site"] == "YouTube" and r["type"] == "Trailer":
                return r["key"]

        for r in list_result:
            if r["site"] == "YouTube" and r["type"] == "Teaser":
                return r["key"]

        return None






