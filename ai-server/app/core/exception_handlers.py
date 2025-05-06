from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AIServerError
from app.core.response import error_response


# HTTPException 처리 핸들러
async def ai_server_error_handler(request: Request, exc: AIServerError):
    response = error_response(message=exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )
