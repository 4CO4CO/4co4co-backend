from fastapi.responses import JSONResponse
from fastapi import Request
from app.utils.exceptions import AIServerError
from app.utils.response import error_response


async def ai_server_error_handler(request: Request, exc: AIServerError):

    response = error_response(
        message=exc.message,
        error_code=exc.error_code
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump()
    )
