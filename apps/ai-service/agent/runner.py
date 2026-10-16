from typing import cast

from fastapi import HTTPException
from openai import APIError, AsyncOpenAI
from openai.types.responses import ResponseInputParam, ResponseInputItemParam
from openai.types.responses.response_input_param import FunctionCallOutput
from agent.prompt import build_instructions
from domain.schemas.assistant import CreateReservation, AssistantResponse, ReservationInfo
from service.assistant import AssistantService
from core.config import settings
from agent.tools import TOOLS

import json

async def execute_tool(name: str, arguments: dict, ai_service: AssistantService, user_id: str | None = None):
    if name == "search_showtimes":
        return await ai_service.search_showtimes(**arguments)

    if name == "create_reservation":
        return await ai_service.create_reservation(CreateReservation(**arguments), user_id=user_id)

    if name == "get_seats_map":
        return await ai_service.get_seats_map(**arguments)

    raise ValueError(f"Unknown tool {name}")


async def run_agent(
        message: str,
        ai_service: AssistantService,
        openai_client: AsyncOpenAI,
        conversation_id: str,
        history: ResponseInputParam,
        user_id: str | None = None
) -> tuple[AssistantResponse, ResponseInputParam]:

    instructions = build_instructions(user_id is not None)

    items: ResponseInputParam = list(history)
    items.append({"role":"user", "content":message})


    response = await openai_client.responses.create(
        model=settings.openai_model,
        instructions=instructions,
        input=items,
        tools=TOOLS,
        max_output_tokens=settings.max_output_tokens,
        store=False
    )
    reservation: ReservationInfo | None = None
    seat_map_screening_id: int | None = None

    for round_number in range(settings.max_tool_rounds):

        items.extend(cast(ResponseInputItemParam, item.model_dump(mode="json", exclude={"id"}, exclude_none=True)) for item in response.output)

        calls = [
            item for item in response.output if item.type == "function_call"
        ]

        if len(calls) == 0:
            return AssistantResponse(
                answer=response.output_text,
                conversation_id=conversation_id,
                reservation=reservation,
                seats_map_screening_id=seat_map_screening_id
            ), _trim_history(items)

        tool_outputs: ResponseInputParam = []

        for call in calls:
            try:
                arguments = json.loads(call.arguments)
                result = await execute_tool(call.name, arguments, ai_service, user_id)
                if call.name == "create_reservation":
                    reservation = ReservationInfo(group_id=result[0].group_id, guest_email=result[0].guest_email)
                if isinstance(result, list):
                    output = json.dumps([item.model_dump(mode="json") for item in result])
                else:
                    output = result.model_dump_json()

                if call.name == "get_seats_map":
                    seat_map_screening_id = arguments["screening_id"]

            except HTTPException as e:
                output = json.dumps({"error": e.detail})

            except ValueError as e:
                output = json.dumps({"error": str(e)})

            tool_outputs.append(FunctionCallOutput(
                type="function_call_output",
                call_id=call.call_id,
                output=output,
                )
            )
        items.extend(tool_outputs)

        try:
            response = await openai_client.responses.create(
                model=settings.openai_model,
                instructions=instructions,
                input=items,
                tools=TOOLS,
                tool_choice="none" if round_number == settings.max_tool_rounds - 1 else "auto",
                max_output_tokens=settings.max_output_tokens,
                store=False
            )
        except APIError:
            if reservation is None:
                raise
            return AssistantResponse(
                answer="Rezerwacja utworzona. Opłać ją przyciskiem poniżej.",
                conversation_id=conversation_id,
                reservation=reservation,
                seats_map_screening_id=seat_map_screening_id
            ), _trim_history(items)

    items.extend(cast(ResponseInputItemParam, item.model_dump(mode="json", exclude={"id"}, exclude_none=True)) for item in response.output)

    return AssistantResponse(
        answer=response.output_text,
        conversation_id=conversation_id,
        reservation=reservation,
        seats_map_screening_id=seat_map_screening_id
    ), _trim_history(items)


def _trim_history(items: ResponseInputParam) -> ResponseInputParam:
    if len(items) <= settings.max_history_items:
        return items

    trimmed = items[-settings.max_history_items:]

    for index, item in enumerate(trimmed):
        if item.get("role") == "user":
            return trimmed[index:]

    return trimmed