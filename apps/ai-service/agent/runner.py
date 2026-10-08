from openai.types.responses import ResponseInputParam
from openai.types.responses.response_input_param import FunctionCallOutput

from agent.prompt import build_instructions
from service.assistant import AssistantService
from core.config import settings
from agent.tools import TOOLS

import json

async def execute_tool(name: str, arguments: dict, ai_service: AssistantService):
    if name == "search_showtimes":
        return await ai_service.search_showtimes(**arguments)

    raise ValueError(f"Unknown tool {name}")


async def run_agent(message: str, ai_service: AssistantService, previous_response_id: str | None = None) -> dict[str, str]:
    instructions = build_instructions()

    response = await settings.openai_client.responses.create(
        model=settings.openai_model,
        instructions=instructions,
        previous_response_id=previous_response_id,
        input=message,
        tools=TOOLS,
    )

    while True:
        calls = [
            item for item in response.output if item.type == "function_call"
        ]

        if len(calls) == 0:
            return {"answer": response.output_text, "response_id": response.id}

        tool_outputs: ResponseInputParam = []

        for call in calls:
            arguments = json.loads(call.arguments)
            result = await execute_tool(call.name, arguments, ai_service)

            tool_outputs.append(FunctionCallOutput(
                type="function_call_output",
                call_id=call.call_id,
                output=json.dumps([item.model_dump() for item in result]),
            )
        )

        response = await settings.openai_client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
        )
