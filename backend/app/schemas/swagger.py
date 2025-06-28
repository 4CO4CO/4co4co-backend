from app.schemas.response.schemas import ErrorResponseModel, ResponseModel

success_200_create_lantern = {
    "description": "Lantern successfully created",
    "model": ResponseModel,
    "content": {
        "application/json": {
            "example": {
                "status": "success",
                "message": "Lantern Created",
                "data": {
                    "lantern_id": "4co4co-1234"
                }
            }
        }
    }
}


error_400_lantern_examples = {
    "description": "랜턴 생성 관련 400 Bad Request",
    "model": ErrorResponseModel,
    "content": {
        "application/json": {
            "examples": {
                "INVALID_INPUT_FORMAT": {
                    "summary": "입력 형식 오류 (예: multipart 아님, boolean 필드 문제 등)",
                    "value": {
                        "status": "error",
                        "error_code": "INVALID_INPUT_FORMAT",
                        "message": "입력 형식이 올바르지 않습니다."
                    }
                },
                "LANTERN_VALIDATION_FAILED": {
                    "summary": "이름, 설명 등 입력값이 유효하지 않음",
                    "value": {
                        "status": "error",
                        "error_code": "LANTERN_VALIDATION_FAILED",
                        "message": "입력값을 확인해주세요."
                    }
                },
                "INVALID_IMAGE_COUNT": {
                    "summary": "이미지가 3장이 아님",
                    "value": {
                        "status": "error",
                        "error_code": "INVALID_IMAGE_COUNT",
                        "message": "이미지는 정확히 3장을 업로드해야 합니다."
                    }
                },
                "INVALID_IMAGE_TYPE": {
                    "summary": "이미지 확장자가 허용되지 않음",
                    "value": {
                        "status": "error",
                        "error_code": "INVALID_IMAGE_TYPE",
                        "message": "이미지 파일 형식이 유효하지 않습니다."
                    }
                },
                "INVALID_FILE_SIZE": {
                    "summary": "이미지 크기가 5MB를 초과함",
                    "value": {
                        "status": "error",
                        "error_code": "INVALID_FILE_SIZE",
                        "message": "파일 크기가 5MB를 초과합니다."
                    }
                }
            }
        }
    }
}


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

error_403 = {
    "description": "LANTERN_NOT_PUBLIC",
    "model": ErrorResponseModel,
    "content": {
        "application/json": {
            "example": {
                "status": "error",
                "error_code": "LANTERN_NOT_PUBLIC",
                "message": "비공개 랜턴입니다."
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
