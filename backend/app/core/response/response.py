from typing import Any

from fastapi.responses import JSONResponse

from app.schemas.response.schemas import ResponseModel, ErrorResponseModel


def success_response(data: Any, message: str = "Success"):
    return ResponseModel(
        status="success",
        message=message,
        data=data
    )


def error_response(message: str = "An error occurred", error_code: str = "UNKNOWN_ERROR"):
    return ErrorResponseModel(
        status="error",
        error_code=error_code,
        message=message
    )


def success_no_cache_response(data, message="Success"):
    return JSONResponse(
        content={"message": message, "data": data},
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )