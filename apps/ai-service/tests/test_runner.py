from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from agent.runner import execute_tool, run_agent
import pytest
import json


@pytest.fixture()
def assist_service() -> AsyncMock:
    return AsyncMock()


async def test_execute_tool_success(assist_service: AsyncMock) -> None:
    assist_service.search_showtimes.return_value = ["search_showtimes"]

    result = await execute_tool(
        "search_showtimes",
        {"city": "Test City", "genre": "Test genre", "after": datetime.now(), "before": datetime.now()},
        assist_service
    )

    assert result == ["search_showtimes"]


async def test_execute_tool_value_error(assist_service: AsyncMock) -> None:
    with pytest.raises(ValueError):

        await execute_tool(
            "bad_name",
            {"city": "Test City", "genre": "Test genre", "after": datetime.now(), "before": datetime.now()},
            assist_service
            )


@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:
    mock_settings.openai_client.responses.create.return_value = SimpleNamespace(output=[], output_text="Test Answer", id="resp_1")

    result = await run_agent("Test", assist_service)

    assert result == {"answer": "Test Answer", "response_id": "resp_1"}


@patch("agent.runner.settings", new_callable=AsyncMock)
async def test_run_agent_call(mock_settings: AsyncMock, assist_service: AsyncMock) -> None:

    call = SimpleNamespace(
        type="function_call", name="search_showtimes", call_id="call_1", arguments=json.dumps({"city": "Test City"}
      ))

    first_response = SimpleNamespace(output=[call], id="resp_1")
    second_response = SimpleNamespace(output=[], output_text="Test Answer", id="resp_2")

    mock_settings.openai_client.responses.create.side_effect = [first_response, second_response]

    result = await run_agent("Test", assist_service)

    assert result == {"answer": "Test Answer", "response_id": "resp_2"}
