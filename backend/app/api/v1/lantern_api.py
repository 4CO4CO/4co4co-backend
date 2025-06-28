import re
from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Path

from app.core.db.database import get_mongo_client
from app.core.response.response import success_response
from app.core.validation.lantern_validation import validate_name, validate_description, validate_images
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel
from app.schemas.response.schemas import ResponseModel
from app.schemas.swagger import error_400, error_403, error_404, error_500
from app.services.lantern_service import LanternService

router = APIRouter()


@router.post(
    "/lanterns",
    responses={
        200: {"description": "Lantern successfully created"},
        400: {"description": "Bad Request - Validation failed (invalid format, oversized file)"},
        422: {"description": "Unprocessable Entity - Missing required fields or wrong types"},
        500: {"description": "Internal Server Error"}
    }
)
async def create_lanterns(
    name: str = Form(..., min_length=1, max_length=50, description="사용자 이름 (1~50자)"),
    description: str = Form(..., description="이미지에 대한 설명"),
    images: List[UploadFile] = File(..., description="이미지 파일 (jpg, jpeg, png, webp, 각 5MB 이하, 총 3장)"),
    is_public: bool = Form(True, description="랜턴을 공개할지 여부"),
    db=Depends(get_mongo_client)
):
    validate_name(name)
    validate_description(description)
    validate_images(images)

    lantern_service = LanternService(db)
    lantern_id = await lantern_service.create_lanterns(
        name=name,
        description=description,
        images=images,
        is_public=is_public
    )

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
            regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"
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
