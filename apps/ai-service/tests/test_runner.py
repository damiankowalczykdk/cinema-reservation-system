from datetime import datetime, timezone, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx2
from fastapi import HTTPException
from openai import APIError
from openai.types.responses import ResponseFunctionToolCall, ResponseInputParam

from agent.runner import execute_tool, run_agent, _trim_history
import pytest
import json

from core.config import settings
from domain.schemas.assistant import AssistantResponse, ShowtimeRead, ReservationRead, ReservationInfo, SeatMapRead


@pytest.fixture()
def assist_service() -> AsyncMock:
    return AsyncMock()

@pytest.fixture()
def openai_client() -> AsyncMock:
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


async def test_run_agent(assist_service: AsyncMock, openai_client: AsyncMock) -> None:
    openai_client.responses.create.return_value = SimpleNamespace(
        output=[], output_text="Test Answer")

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(answer="Test Answer", conversation_id="conversation_id")
    assert items == [{"role": "user", "content": "Test"}]


async def test_run_agent_call(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="search_showtimes",
        call_id="call_1",
        arguments=json.dumps({"city": "Test City"}
      ))

    first_response = SimpleNamespace(output=[call])
    second_response = SimpleNamespace(output=[], output_text="Test Answer")

    assist_service.search_showtimes.return_value = [ShowtimeRead(
        screening_id=1,
        movie_title="Test Movie",
        cinema_name="Test Cinema",
        city="Test City",
        genre="animation",
        start_time=datetime.now(timezone.utc),
        price=Decimal("25"),
    )]

    openai_client.responses.create.side_effect = [first_response, second_response]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(answer="Test Answer", conversation_id="conversation_id")
    assert [item.get("type", item.get("role")) for item in items] == ["user", "function_call", "function_call_output"]

async def test_run_agent_stops_after_max_tool(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="search_showtimes",
        call_id="call_1",
        arguments=json.dumps({"city": "Test City"}
      ))

    first_response = SimpleNamespace(output=[call])
    second_response = SimpleNamespace(output=[], output_text="Test Answer")

    assist_service.search_showtimes.return_value = [ShowtimeRead(
        screening_id=1,
        movie_title="Test Movie",
        cinema_name="Test Cinema",
        city="Test City",
        genre="animation",
        start_time=datetime.now(timezone.utc),
        price=Decimal("25"),
    )]

    openai_client.responses.create.side_effect = [
        first_response,
        first_response,
        first_response,
        first_response,
        first_response,
        second_response
    ]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(answer="Test Answer", conversation_id="conversation_id")
    assert [item.get("type", item.get("role")) for item in items] == ["user"] + ["function_call", "function_call_output"] * 5

async def test_run_agent_raises_when_llm_fails_without_reservation(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="search_showtimes",
        call_id="call_1",
        arguments=json.dumps({"city": "Test City"}
      ))

    first_response = SimpleNamespace(output=[call])


    assist_service.search_showtimes.return_value = [ShowtimeRead(
        screening_id=1,
        movie_title="Test Movie",
        cinema_name="Test Cinema",
        city="Test City",
        genre="animation",
        start_time=datetime.now(timezone.utc),
        price=Decimal("25"),
    )]

    openai_client.responses.create.side_effect = [
        first_response,
        APIError("boom", httpx2.Request("POST", "http://test"), body=None)]

    with pytest.raises(APIError):
        await run_agent("Test", assist_service, openai_client, "conversation_id", [])


async def test_run_agent_returns_reservation_when_llm_fails(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [{"row": 1, "seat": 1}], "guest_email": "test@example.com", "guest_name": ""}
      ))

    first_response = SimpleNamespace(output=[call])


    assist_service.create_reservation.return_value = [ReservationRead(
        group_id=1,
        screening_id=1,
        guest_email="test@example.com",
        row=1,
        seat=1,
        status="pending",
        price_paid=Decimal("25"),
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=15))
    )]

    openai_client.responses.create.side_effect = [
        first_response,
        APIError("boom", httpx2.Request("POST", "http://test"), body=None)]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(
        answer="Rezerwacja utworzona. Opłać ją przyciskiem poniżej.",
        conversation_id="conversation_id",
        reservation=ReservationInfo(group_id=1, guest_email="test@example.com"),
    )
    assert [item.get("type", item.get("role")) for item in items] == ["user", "function_call", "function_call_output"]


async def test_run_agent_create_reservation(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [{"row": 1, "seat": 1}], "guest_email": "test@example.com", "guest_name": ""}

      ))

    first_response = SimpleNamespace(output=[call])
    second_response = SimpleNamespace(output=[], output_text="Test Answer")

    assist_service.create_reservation.return_value = [ReservationRead(
        group_id=1,
        screening_id=1,
        guest_email="test@example.com",
        row=1,
        seat=1,
        status="pending",
        price_paid=Decimal("25"),
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=15))
    )]

    openai_client.responses.create.side_effect = [first_response, second_response]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(
        answer="Test Answer",
        conversation_id="conversation_id",
        reservation=ReservationInfo(group_id=1, guest_email="test@example.com")
    )


async def test_run_agent_create_reservation_user_logged(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [{"row": 1, "seat": 1}]},
      ))

    first_response = SimpleNamespace(output=[call])
    second_response = SimpleNamespace(output=[], output_text="Test Answer")

    assist_service.create_reservation.return_value = [ReservationRead(
        group_id=1,
        screening_id=1,
        guest_email=None,
        row=1,
        seat=1,
        status="pending",
        price_paid=Decimal("25"),
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=15))
    )]

    openai_client.responses.create.side_effect = [first_response, second_response]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [], user_id="example_user_id")

    assert result == AssistantResponse(answer="Test Answer", conversation_id="conversation_id", reservation=ReservationInfo(group_id=1))


async def test_run_agent_create_reservation_error(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [{"row": 1, "seat": 1}], "guest_email": "test@example.com", "guest_name": ""}

      ))

    first_response = SimpleNamespace(output=[call])
    second_response = SimpleNamespace(output=[], output_text="Test Answer")

    assist_service.create_reservation.side_effect = HTTPException(
        status_code=409,
        detail="BOOM"
    )

    openai_client.responses.create.side_effect = [first_response, second_response]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(answer="Test Answer", conversation_id="conversation_id", reservation=None)

async def test_run_agent_create_reservation_error_empty_seats(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="create_reservation",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1, "seats": [], "guest_email": "test@example.com", "guest_name": ""}

      ))

    first_response = SimpleNamespace(output=[call])
    second_response = SimpleNamespace(output=[], output_text="Test Answer")

    openai_client.responses.create.side_effect = [first_response, second_response]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(answer="Test Answer", conversation_id="conversation_id", reservation=None)

    assist_service.create_reservation.assert_not_called()


async def test_run_agent_get_seats_map(assist_service: AsyncMock, openai_client: AsyncMock) -> None:

    call = ResponseFunctionToolCall(
        type="function_call",
        name="get_seats_map",
        call_id="call_1",
        arguments=json.dumps({"screening_id": 1}

      ))

    first_response = SimpleNamespace(output=[call])
    second_response = SimpleNamespace(output=[], output_text="Test Answer")

    assist_service.get_seats_map.return_value = SeatMapRead(
        seats=[(1,1)],
        row=1,
        seat_per_row=1
    )

    openai_client.responses.create.side_effect = [first_response, second_response]

    result, items = await run_agent("Test", assist_service, openai_client, "conversation_id", [])

    assert result == AssistantResponse(answer="Test Answer", conversation_id="conversation_id", seats_map_screening_id=1)


def test_trim_history_returns_items_when_under_limit(monkeypatch) -> None:
    monkeypatch.setattr("agent.runner.settings", settings.model_copy(update={"max_history_items": 3}))

    items: ResponseInputParam = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hello"}]

    res = _trim_history(items)

    assert len(res) == 2
    assert res == items

def test_trim_history_returns_items_when_over_limit(monkeypatch) -> None:
    monkeypatch.setattr("agent.runner.settings", settings.model_copy(update={"max_history_items": 2}))

    items: ResponseInputParam = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hello"}, {"role": "user", "content": "Test"}]

    res = _trim_history(items)

    assert len(res) == 1
    assert res == items[-1:]

def test_trim_history_returns_trimmed_when_no_user_message(monkeypatch) -> None:
    monkeypatch.setattr("agent.runner.settings", settings.model_copy(update={"max_history_items": 1}))

    items: ResponseInputParam = [{"role": "assistant", "content": "Hello"}, {"role": "assistant", "content": "Hello2"}]

    res = _trim_history(items)

    assert len(res) == 1
    assert res == items[-1:]




