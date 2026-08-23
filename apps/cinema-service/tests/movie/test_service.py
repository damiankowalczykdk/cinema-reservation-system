import pytest
from datetime import date
from unittest.mock import AsyncMock

from core.exceptions import ConflictException, NotFoundException
from domain.models.movie import Genre, Movie
from domain.schemas.movie import CreateMovie, MovieRead, UpdateMovie
from services.movie import MovieService


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()

@pytest.fixture
def movie_service(mock_repo: AsyncMock) -> MovieService:
    return MovieService(mock_repo)

async def test_create_movie_success(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    mock_repo.get_movie_by_title_and_release_date = AsyncMock(return_value=None)

    create_movie = CreateMovie(
        title="Test Movie Title",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8,23)
    )


    await movie_service.create_movie(create_movie)

    mock_repo.add.assert_called_once()
    mock_repo.get_movie_by_title_and_release_date.assert_awaited_with("Test Movie Title", date(2026,8,23))

    result = mock_repo.add.call_args[0][0]

    assert result is not None
    assert result.title == "Test Movie Title"
    assert result.description == "Test Movie Description"
    assert result.duration_minutes == 60


async def test_create_movie_if_already_exist(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    mock_repo.get_movie_by_title_and_release_date = AsyncMock(return_value=True)

    create_movie = CreateMovie(
        title="Test Movie Title",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8,23)
    )

    with pytest.raises(ConflictException, match="Movie already exists"):
        await movie_service.create_movie(create_movie)


async def test_get_movie_by_id_success(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    movie = MovieRead(
        id=1,
        title="Test Movie Title",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8,23)
    )
    mock_repo.get_by_id = AsyncMock(return_value=movie)


    result = await movie_service.get_movie_by_id(1)

    assert result.title == "Test Movie Title"

async def test_get_movie_by_id_not_found(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Movie not found"):
        await movie_service.get_movie_by_id(1)

async def test_get_movie_by_title_success(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    movie = MovieRead(
        id=1,
        title="Test Movie Title",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8,23)
    )
    mock_repo.get_movie_by_title = AsyncMock(return_value=[movie])


    result = await movie_service.get_movie_by_title("Test Movie Title")

    assert result[0].title == "Test Movie Title"

async def test_get_movie_by_title_not_found(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    mock_repo.get_movie_by_title = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Movie not found"):
        await movie_service.get_movie_by_title("Test Movie Title")


async def test_update_movie_success(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    movie = Movie(
        id=1,
        title="Test Movie Title",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8,23)
    )

    mock_repo.get_by_id = AsyncMock(return_value=movie)
    mock_repo.get_movie_by_title_and_release_date = AsyncMock(return_value=None)

    update_movie = UpdateMovie(
        title="Test Movie Title2",
    )

    await movie_service.update_movie(1, update_movie)

    result = mock_repo.add.call_args[0][0]

    assert result.title == "Test Movie Title2"
    assert repr(movie) == "< Movie 1 title: Test Movie Title2 description: Test Movie Description duration: 60 genre: Genre.CRIME release_date: 2026-08-23 >"


async def test_update_movie_if_already_exist(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    movie = Movie(
        id=1,
        title="Test Movie Title",
        description="Test Movie Description",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026,8,23)
    )

    movie_2 = Movie(
        id=2,
        title="Test Movie Title2",
        description="Test Movie Description2",
        duration_minutes=60,
        genre=Genre.CRIME,
        release_date=date(2026, 8, 23)
    )

    mock_repo.get_by_id = AsyncMock(return_value=movie)
    mock_repo.get_movie_by_title_and_release_date = AsyncMock(return_value=movie_2)

    update_movie = UpdateMovie(
        title="Test Movie Title2",
    )

    with pytest.raises(ConflictException, match="Movie already exists"):
        await movie_service.update_movie(1, update_movie)

async def test_update_movie_not_found(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=None)

    update_movie = UpdateMovie(
        title="Test Movie Title2",
    )

    with pytest.raises(NotFoundException, match="Movie not found"):
        await movie_service.update_movie(1, update_movie)

async def test_delete_movie_by_id_success(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=True)

    await movie_service.delete_movie_by_id(1)

    mock_repo.delete_by_id.assert_awaited_with(1)


async def test_delete_movie_by_id_not_found(movie_service: MovieService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="Movie not found"):
        await movie_service.delete_movie_by_id(1)

