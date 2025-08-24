from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.exceptions import AIServerError
from app.core.response import error_response


async def ai_server_error_handler(request: Request, exc: AIServerError):
    """
    Custom exception handler for AIServerError.

    Args:
        request (Request): Incoming HTTP request that caused the error
        exc (AIServerError): The exception instance

    Returns:
        JSONResponse: HTTP response with standardized error payload
    """
    response = error_response(
        message=exc.message,
        error_code=exc.error_code
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump()
    )
