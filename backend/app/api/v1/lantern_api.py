from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Path

from app.core.db.database import get_mongo_client
from app.core.exceptions.types import ValidationError
from app.core.response.response import success_response
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel
from app.schemas.response.schemas import ResponseModel
from app.schemas.swagger import error_400, error_403, error_404, error_500
from app.services.lantern_service import LanternService

router = APIRouter()

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
MAX_FILE_SIZE_MB = 5


@router.post(
    "/lanterns",
    responses={
        200: {"description": "Lantern successfully created"},
        400: {"description": "Bad Request - Validation failed (blank name, invalid format, oversized file)"},
        422: {"description": "Unprocessable Entity - Missing required fields or wrong types"},
        500: {"description": "Internal Server Error"}
    }
)
async def create_lanterns(
    name: str = Form(..., min_length=1, max_length=50, description="Lantern name (1-50 characters)"),
    image: UploadFile = File(..., description="Image file (jpg, jpeg, png, webp, max 5MB)"),
    db=Depends(get_mongo_client)
):
    if not name.strip():
        raise ValidationError("Lantern name cannot be blank.")

    if len(name) > 50:
        raise ValidationError("Lantern name must be 50 characters or less.")

    if not any(image.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValidationError("Unsupported image format. Allowed: jpg, jpeg, png, webp.")

    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")

    lantern_service = LanternService(db)
    lantern_id = await lantern_service.create_lanterns(name, image)
    return success_response(data={"lantern_id": lantern_id}, message="Lantern Created")


@router.get(
    "/lanterns",
    response_model=ResponseModel[List[LanternResponseModel]],
    responses={
        200: {"description": "Lantern List"},
        400: error_400,
        404: error_404,
        500: error_500
    }
)
async def get_lantern_list(
        current_lantern_id: Optional[str] = Query(
            None,
            description="현재 체험 중인 사용자 랜턴 ID",
            regex = r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"
        ), db=Depends(get_mongo_client)
):
    lantern_service = LanternService(db)
    lanterns = await lantern_service.get_recent_lanterns(current_lantern_id=current_lantern_id)
    return success_response(
        data=[lantern.model_dump() for lantern in lanterns],
        message="Lantern list"
    )


@router.get(
    "/lanterns/{lantern_id}",
    response_model=ResponseModel[LanternDetailResponseModel],
    responses={
        200: {"description": "Lantern Detail"},
        400: error_400,
        403: error_403,
        404: error_404,
        500: error_500
    }
)
async def get_lantern_detail(
        lantern_id: str = Path(
            ...,
            description="조회할 랜턴의 ID",
            regex = r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"
        ),
        db=Depends(get_mongo_client)
):
    lantern_service = LanternService(db)
    lantern = await lantern_service.get_lantern_detail(lantern_id)
    return success_response(
        data=lantern.model_dump(),
        message="Lantern detail"
    )
