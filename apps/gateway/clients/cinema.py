from fastapi import HTTPException
from api.dependencies import CinemaServiceClientDep

async def get_cinema_health(cinema_client: CinemaServiceClientDep) -> dict:
    try:
        return await cinema_client.safe_request("GET", "/health")
    except HTTPException as e:
        return {"status": "unreachable", "message": str(e.detail)}
