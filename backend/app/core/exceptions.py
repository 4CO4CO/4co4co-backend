from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.response import error_response


# HTTPException 처리 핸들러
# 예: raise HTTPException(status_code=400, detail="Name is required")에서 발생
async def http_exception_handler(request: Request, exc: HTTPException):
    response = error_response(message=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


# RequestValidationError 처리 핸들러
# 예: 필수 필드 누락, 잘못된 타입 등 Pydantic 유효성 검증에서 발생 (422 상태)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]["msg"] if exc.errors() else "Invalid request"
    response = error_response(message=first_error)
    return JSONResponse(
        status_code=422,
        content=response.dict()
    )