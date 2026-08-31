from fastapi import APIRouter, status
from domain.schemas.movie import MovieRead, CreateMovie, UpdateMovie
from api.dependencies import CinemaServiceClientDep, admin

router = APIRouter(prefix="/movies", tags=["movies"])

@router.post("/", response_model=MovieRead, status_code=status.HTTP_201_CREATED, summary="Create Movie", dependencies=[admin])
async def create_movie(payload: CreateMovie, movie_client: CinemaServiceClientDep) -> MovieRead:
    return await movie_client.safe_request("POST", f"/movie/", json=payload.model_dump(mode="json"))

@router.get("/{movie_id}", response_model=MovieRead, status_code=status.HTTP_200_OK ,summary="Get Movie", dependencies=[admin])
async def get_movie_by_id(movie_id: int, movie_client: CinemaServiceClientDep) -> MovieRead:
    return await movie_client.safe_request("GET", f"/movie/{movie_id}")

@router.get("/", response_model=list[MovieRead], status_code=status.HTTP_200_OK, summary="Get Movies", dependencies=[admin])
async def get_movie_by_title(title: str, movie_client: CinemaServiceClientDep) -> list[MovieRead]:
    return await movie_client.safe_request("GET", f"/movie/", params={"title": title})


@router.patch("/{movie_id}", response_model=MovieRead, status_code=status.HTTP_200_OK, summary="Update Movie", dependencies=[admin])
async def update_movie(movie_id: int, payload: UpdateMovie, movie_client: CinemaServiceClientDep) -> MovieRead:
    return await movie_client.safe_request("PATCH", f"/movie/{movie_id}", json=payload.model_dump(mode="json"))


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Movie", dependencies=[admin])
async def delete_movie(movie_id: int, movie_client: CinemaServiceClientDep) -> None:
    await movie_client.request("DELETE", f"/movie/{movie_id}")
