import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions.types import AppError
from app.core.response.response import error_response

# 로거 설정
logger = logging.getLogger("uvicorn.error")


# RequestValidationError 처리 핸들러 (400 Bad Request)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]["msg"] if exc.errors() else "입력 형식이 올바르지 않습니다."
    response = error_response(
        message="입력 형식이 올바르지 않습니다.",
        error_code="INVALID_INPUT_FORMAT"
    )

    logger.warning(
        "[ValidationError] %s %s | Error: %s | Response: %s",
        request.method,
        request.url.path,
        first_error,
        response.dict()
    )

    return JSONResponse(
        status_code=400,
        content=response.dict()
    )


# AppError (커스텀 예외) 처리 핸들러
async def app_error_handler(request: Request, exc: AppError):
    status_code = getattr(exc, 'status_code', 500)
    error_code = getattr(exc, 'error_code', 'UNKNOWN_ERROR')
    message = str(exc)

    response = error_response(
        message=message,
        error_code=error_code
    )

    logger.error(
        "[AppError] %s %s | ErrorCode: %s | Message: %s | Response: %s",
        request.method,
        request.url.path,
        error_code,
        message,
        response.dict()
    )

    return JSONResponse(
        status_code=status_code,
        content=response.dict()
    )


# 500 Internal Server Error용 핸들러
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"[Unhandled Exception] {request.method} {request.url.path} - {exc}")
    response = error_response(
        message="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        error_code="INTERNAL_SERVER_ERROR"
    )
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )
