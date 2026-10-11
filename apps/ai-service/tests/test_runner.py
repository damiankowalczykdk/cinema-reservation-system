from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from agent.runner import execute_tool, run_agent
import pytest
import json

from domain.schemas.assistant import AssistantResponse, ShowtimeRead, ReservationRead, ReservationInfo, SeatMapRead


@pytest.fixture()
def assist_service() -> AsyncMock:
    return AsyncMock()


async def test_execute_tool_search_showetimes_success(assist_service: AsyncMock) -> None:
    assist_service.search_showtimes.return_value = ["search_showtimes"]

    result = await execute_tool(
        "search_showtimes",
        {"city": "Test City", "genre": "Test genre", "after": datetime.now(), "before": datetime.now()},
        assist_service
    )

    assert result == ["search_showtimes"]

async def test_execute_tool_create_reservation_success(assist_service: AsyncMock) -> None:
    assist_service.create_reservation.return_value = ["create_reservation"]

    result = await execute_tool(
        "create_reservation",
        {"screening_id": 1, "seats": [{"row":1, "seat": 1}], "guest_email": "test@example.com", "guest_name": ""},
        assist_service
    )

    assert result == ["create_reservation"]

async def test_execute_get_seat_map_success(assist_service: AsyncMock) -> None:
    assist_service.get_seats_map.return_value = ["get_seats_map"]

    result = await execute_tool(
        "get_seats_map",
        {"screening_id": 1},
        assist_service
    )

    assert result == ["get_seats_map"]


async def test_execute_tool_value_error(assist_service: AsyncMock) -> None:
    with pytest.raises(ValueError):

        await execute_tool(
            "bad_name",
            {"city": "Test City", "genre": "Test genre", "after": datetime.now(), "before": datetime.now()},
            assist_service
            )


@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:
    mock_settings.openai_client.responses.create.return_value = SimpleNamespace(
        output=[], output_text="Test Answer", id="resp_1")

    result = await run_agent("Test", assist_service)

    assert result == AssistantResponse(answer="Test Answer", response_id="resp_1")


@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent_call(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:

    call = SimpleNamespace(
        type="function_call",
        name="search_showtimes",
        call_id="call_1",
        arguments=json.dumps({"city": "Test City"}
      ))

    first_response = SimpleNamespace(output=[call], id="resp_1")
    second_response = SimpleNamespace(output=[], output_text="Test Answer", id="resp_2")

    assist_service.search_showtimes.return_value = [ShowtimeRead(
        screening_id=1,
        movie_title="Test Movie",
        cinema_name="Test Cinema",
        city="Test City",
        genre="animation",
        start_time=datetime.now(timezone.utc),
        price=Decimal("25"),
    )]

    mock_settings.openai_client.responses.create.side_effect = [first_response, second_response]

    result = await run_agent("Test", assist_service)

    assert result == AssistantResponse(answer="Test Answer", response_id="resp_2")



@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent_create_reservation(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:

    call = SimpleNamespace(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [{"row": 1, "seat": 1}], "guest_email": "test@example.com", "guest_name": ""}

      ))

    first_response = SimpleNamespace(output=[call], id="resp_1")
    second_response = SimpleNamespace(output=[], output_text="Test Answer", id="resp_2")

    assist_service.create_reservation.return_value = [ReservationRead(
        group_id=1,
        screening_id=1,
        guest_email="test@example.com",
        row=1,
        seat=1,
        status="pending",
        price_paid=Decimal("25")
    )]

    mock_settings.openai_client.responses.create.side_effect = [first_response, second_response]

    result = await run_agent("Test", assist_service)

    assert result == AssistantResponse(answer="Test Answer", response_id="resp_2", reservation=ReservationInfo(group_id=1, guest_email="test@example.com"))

@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent_create_reservation_user_logged(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:

    call = SimpleNamespace(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [{"row": 1, "seat": 1}]},
      ))

    first_response = SimpleNamespace(output=[call], id="resp_1")
    second_response = SimpleNamespace(output=[], output_text="Test Answer", id="resp_2")

    assist_service.create_reservation.return_value = [ReservationRead(
        group_id=1,
        screening_id=1,
        guest_email=None,
        row=1,
        seat=1,
        status="pending",
        price_paid=Decimal("25")
    )]

    mock_settings.openai_client.responses.create.side_effect = [first_response, second_response]

    result = await run_agent("Test", assist_service, user_id="example_user_id")

    assert result == AssistantResponse(answer="Test Answer", response_id="resp_2", reservation=ReservationInfo(group_id=1))



@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent_create_reservation_error(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:

    call = SimpleNamespace(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [{"row": 1, "seat": 1}], "guest_email": "test@example.com", "guest_name": ""}

      ))

    first_response = SimpleNamespace(output=[call], id="resp_1")
    second_response = SimpleNamespace(output=[], output_text="Test Answer", id="resp_2")

    assist_service.create_reservation.side_effect = HTTPException(
        status_code=409,
        detail="BOOM"
    )

    mock_settings.openai_client.responses.create.side_effect = [first_response, second_response]

    result = await run_agent("Test", assist_service)

    assert result == AssistantResponse(answer="Test Answer", response_id="resp_2", reservation=None)


@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent_get_seats_map(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:

    call = SimpleNamespace(
        type="function_call",
        name="get_seats_map",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1}

      ))

    first_response = SimpleNamespace(output=[call], id="resp_1")
    second_response = SimpleNamespace(output=[], output_text="Test Answer", id="resp_2")

    assist_service.get_seats_map.return_value = SeatMapRead(
        seats=[(1,1)],
        row=1,
        seat_per_row=1
    )

    mock_settings.openai_client.responses.create.side_effect = [first_response, second_response]

    result = await run_agent("Test", assist_service)

    assert result == AssistantResponse(answer="Test Answer", response_id="resp_2", seats_map_screening_id=1)