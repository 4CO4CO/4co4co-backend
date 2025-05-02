from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.response import error_response

async def http_exception_handler(request: Request, exc: HTTPException):
    response = error_response(message=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )
