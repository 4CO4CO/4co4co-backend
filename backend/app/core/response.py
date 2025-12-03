from typing import Any

from fastapi.responses import JSONResponse

from app.schemas.response.schemas import ResponseModel, ErrorResponseModel


def success_response(data: Any, message: str = "Success") -> ResponseModel:
    return ResponseModel(
        status="success",
        message=message,
        data=data
    )


def error_response(message: str = "An error occurred", error_code: str = "UNKNOWN_ERROR") -> ErrorResponseModel:
    return ErrorResponseModel(
        status="error",
        error_code=error_code,
        message=message
    )


def success_no_cache_response(data: Any, message: str = "Success") -> JSONResponse:
    model = success_response(data=data, message=message)

    return JSONResponse(
        content=model.model_dump(mode='json'),
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )