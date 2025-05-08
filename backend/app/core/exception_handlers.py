import logging

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.response import error_response

# 로거 설정
logger = logging.getLogger("uvicorn.error")


# HTTPException 처리 핸들러
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail} (status: {exc.status_code})")
    response = error_response(message=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


# RequestValidationError 처리 핸들러
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]["msg"] if exc.errors() else "Invalid request"
    logger.error(f"RequestValidationError: {first_error}")
    response = error_response(message=first_error)
    return JSONResponse(
        status_code=422,
        content=response.dict()
    )


# AppError (커스텀 예외) 처리 핸들러
async def app_error_handler(request: Request, exc: AppError):
    logger.error(f"AppError: {exc}")
    response = error_response(message=str(exc))
    return JSONResponse(
        status_code=getattr(exc, 'status_code', 500),
        content=response.dict()
    )
