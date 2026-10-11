from fastapi import HTTPException
from openai.types.responses import ResponseInputParam
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
        previous_response_id: str | None = None,
        user_id: str | None = None
) -> AssistantResponse:

    instructions = build_instructions(user_id is not None)

    response = await settings.openai_client.responses.create(
        model=settings.openai_model,
        instructions=instructions,
        previous_response_id=previous_response_id,
        input=message,
        tools=TOOLS,
    )
    reservation: ReservationInfo | None = None
    seat_map_screening_id: int | None = None

    while True:
        calls = [
            item for item in response.output if item.type == "function_call"
        ]

        if len(calls) == 0:
            return AssistantResponse(
                answer=response.output_text,
                response_id=response.id,
                reservation=reservation,
                seats_map_screening_id=seat_map_screening_id
            )

        tool_outputs: ResponseInputParam = []


        for call in calls:
            arguments = json.loads(call.arguments)
            try:
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

            tool_outputs.append(FunctionCallOutput(
                type="function_call_output",
                call_id=call.call_id,
                output=output,
                )
            )

        response = await settings.openai_client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
        )
