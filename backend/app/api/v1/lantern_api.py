from typing import List, Optional

from fastapi import (
    APIRouter, UploadFile, File, Form, Query, Path, Header, Depends, Request
)
from sse_starlette.sse import EventSourceResponse

from app.core.logging.logger import get_logger
from app.core.response import success_response, success_no_cache_response
from app.core.validation.lantern_validation import validate_name, validate_images
from app.api.deps import get_lantern_service
from app.services.lantern_service import LanternService
from app.worker.tasks import process_lantern_music
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel
from app.schemas.response.schemas import ResponseModel
from app.schemas.swagger import (
    error_400, error_403, error_404, error_500,
    error_400_lantern_examples, success_200_create_lantern,
    success_200_music_status
)

logger = get_logger(__name__)

router = APIRouter()


# -----------------------------------------------------------------------------
# 1. Get Music Generation Status (SSE)
# -----------------------------------------------------------------------------
@router.get(
    "/lanterns/{lantern_id}/music-status",
    responses={
        200: success_200_music_status,
        400: {"description": "Invalid parameters"},
        404: {"description": "Lantern not found"},
    },
)
async def music_status(
        request: Request,
        lantern_id: str = Path(..., regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"),
        resume: bool = Query(False),
        last_event_id: Optional[str] = Header(None, convert_underscores=False),
        service: LanternService = Depends(get_lantern_service),
):
    """
    Streams music generation progress to the client via SSE.
    """
    logger.info(f"[music_status] Req: {lantern_id}, resume={resume}")

    return EventSourceResponse(
        service.subscribe_music_status(
            request=request,
            lantern_id=lantern_id,
            resume=resume,
            last_event_id=last_event_id
        ),
        ping=15
    )


# -----------------------------------------------------------------------------
# 2. Create Lantern & Music Generation
# -----------------------------------------------------------------------------
@router.post(
    "/lanterns",
    status_code=201,
    response_model=ResponseModel[dict],
    responses={
        201: success_200_create_lantern,
        400: error_400_lantern_examples,
        500: error_500,
    },
)
async def create_lanterns(
        name: str = Form(..., min_length=1, max_length=50),
        images: List[UploadFile] = File(...),
        is_public: bool = Form(True),
        service: LanternService = Depends(get_lantern_service),
):
    """
    1. Validates input
    2. Uploads images & Saves metadata to DB
    3. Triggers asynchronous Celery tasks for AI music generation
    """
    logger.info(f"[create_lanterns] Request: name={name}")

    # 1. Validation
    validate_name(name)
    validate_images(images)

    # 2. Save Metadata (S3 + DB)
    lantern_id, uploaded_images = await service.create_lantern_metadata(
        name=name, images=images, is_public=is_public
    )

    # 3. Trigger Async Tasks
    for img_info in uploaded_images:
        process_lantern_music.delay(lantern_id, img_info.s3_key)

    logger.info(f"[create_lanterns] Tasks triggered for {lantern_id}")
    return success_response(
        data={"lantern_id": lantern_id},
        message="Lantern created and music generation started"
    )


# -----------------------------------------------------------------------------
# 3. Get Lantern List
# -----------------------------------------------------------------------------
@router.get(
    "/lanterns",
    response_model=ResponseModel[List[LanternResponseModel]],
    responses={
        200: {"description": "Lantern List"},
        400: error_400,
        404: error_404,
        500: error_500,
    },
)
async def get_lantern_list(
        current_lantern_id: Optional[str] = Query(None, regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"),
        service: LanternService = Depends(get_lantern_service),
):
    logger.info(f"[get_lantern_list] Fetching list, current={current_lantern_id}")

    lanterns = await service.get_recent_lanterns(current_lantern_id=current_lantern_id)
    return success_no_cache_response(
        data=[lantern.model_dump() for lantern in lanterns],
        message="Lantern list"
    )


# -----------------------------------------------------------------------------
# 4. Get Lantern Detail
# -----------------------------------------------------------------------------
@router.get(
    "/lanterns/{lantern_id}",
    response_model=ResponseModel[LanternDetailResponseModel],
    responses={
        200: {"description": "Lantern Detail"},
        400: error_400,
        403: error_403,
        404: error_404,
        500: error_500,
    },
)
async def get_lantern_detail(
        lantern_id: str = Path(..., regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"),
        service: LanternService = Depends(get_lantern_service),
):
    logger.info(f"[get_lantern_detail] Fetching: {lantern_id}")

    lantern = await service.get_lantern_detail(lantern_id)
    return success_response(data=lantern.model_dump(), message="Lantern detail")
