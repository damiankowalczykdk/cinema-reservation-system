from datetime import datetime, timezone
from domain.schemas.assistant import ShowtimeRead


def test_format_start_time() -> None:

    showtime_read = ShowtimeRead(
        screening_id=1,
        movie_title="Test Movie Title",
        cinema_name="Test Cinema Name",
        city="Test City",
        genre="Test Genre",
        start_time=datetime(2026,10, 9,12,0, tzinfo=timezone.utc),
        price=100
    ).model_dump(mode="json")

    assert showtime_read["start_time"] == "Friday 2026-10-09 14:00"






