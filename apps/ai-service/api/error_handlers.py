from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from openai import APITimeoutError, APIConnectionError, APIStatusError
from starlette.responses import JSONResponse

import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI):

    @app.exception_handler(APITimeoutError)
    async def api_timeout_error(_: Request, exc: APITimeoutError) -> JSONResponse:
        logger.exception("Request timed out", exc_info=exc)

        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "error": "LLM_TIMEOUT",
                "message": "Asystent nie zdążył odpowiedzieć. Spróbuj ponownie."
            }
        )

    @app.exception_handler(APIConnectionError)
    async def api_connection_error(_: Request, exc: APIConnectionError) -> JSONResponse:
        logger.exception("Connection error", exc_info=exc)

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "LLM_UNAVAILABLE",
                "message": "Brak połączenia z asystentem. Spróbuj ponownie."
            }
        )

    @app.exception_handler(APIStatusError)
    async def api_status_error(_: Request, exc: APIStatusError) -> JSONResponse:
        logger.exception("AI answer error", exc_info=exc)

        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "error": "LLM_ERROR",
                "message": "Asystent jest chwilowo niedostępny."
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        ]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": "VALIDATION_ERROR",
                "message": details
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error"
            }
        )

