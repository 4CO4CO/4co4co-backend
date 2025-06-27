from app.schemas.response.schemas import ErrorResponseModel

error_400 = {
    "description": "INVALID_INPUT_FORMAT",
    "model": ErrorResponseModel,
    "content": {
        "application/json": {
            "example": {
                "status": "error",
                "error_code": "INVALID_INPUT_FORMAT",
                "message": "입력 형식이 올바르지 않습니다."
            }
        }
    }
}

error_404 = {
    "description": "LANTERN_NOT_FOUND",
    "model": ErrorResponseModel,
    "content": {
        "application/json": {
            "example": {
                "status": "error",
                "error_code": "LANTERN_NOT_FOUND",
                "message": "해당 랜턴을 찾을 수 없습니다."
            }
        }
    }
}

error_500 = {
    "description": "INTERNAL_SERVER_ERROR",
    "model": ErrorResponseModel,
    "content": {
        "application/json": {
            "example": {
                "status": "error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다."
            }
        }
    }
}
