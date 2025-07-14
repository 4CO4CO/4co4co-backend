import asyncio
import json
import time
from typing import Optional, List

from fastapi import APIRouter, UploadFile, File, Form, Query, Path, Request, Header
from sse_starlette.sse import EventSourceResponse

from app.core.config.settings import settings
from app.core.db.database import get_mongo_client
from app.core.exceptions.types import InvalidResumeEventError, NotFoundError
from app.core.response.response import success_response
from app.core.validation.lantern_validation import validate_name, validate_images
from app.repositories.lantern_repository import LanternRepository
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel
from app.schemas.response.schemas import ResponseModel
from app.schemas.swagger import error_400, error_403, error_404, error_500, error_400_lantern_examples, \
    success_200_create_lantern, success_200_music_status
from app.services.lantern_service import LanternService

router = APIRouter()


@router.get(
    "/lanterns/{lantern_id}/music-status",
    responses={
        200: success_200_music_status,
        400: {"description": "Invalid lantern_id format"},
        404: {"description": "Lantern not found"},
        500: {"description": "Internal server error"},
    },
)
async def music_status(
    request: Request,
    lantern_id: str = Path(
        ...,
        description="조회할 랜턴의 ID",
        regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"
    ),
    resume: bool = Query(False, description="이전 이벤트 ID를 기반으로 이어받을지 여부"),
    last_event_id: Optional[str] = Header(None, convert_underscores=False)
):
    db = get_mongo_client(request)
    repo = LanternRepository(db)
    start_time = time.time()
    sent_task_ids = set()

    doc = await repo.find_by_lantern_id(lantern_id)
    if not doc:
        raise NotFoundError("Lantern not found")

    if resume and last_event_id:
        valid_ids = {s["task_id"] for s in doc.get("music_statuses", [])}
        if last_event_id in valid_ids:
            sent_task_ids.add(last_event_id)
        else:
            raise InvalidResumeEventError(last_event_id)

    polling_interval = getattr(settings, 'SSE_POLLING_INTERVAL', 3)

    async def event_generator():
        nonlocal doc
        while True:
            try:
                if await request.is_disconnected():
                    break
                if time.time() - start_time > settings.SSE_TIMEOUT:
                    break

                doc = await repo.find_by_lantern_id(lantern_id)
                if not doc:
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": f"Lantern ID '{lantern_id}' not found"})
                    }
                    break

                statuses = doc.get("music_statuses", [])
                new_completed = [
                    s for s in statuses
                    if s["status"] == "success" and s["task_id"] not in sent_task_ids
                ]
                for s in new_completed:
                    yield {
                        "id": s["task_id"],
                        "event": "music_done_partial",
                        "data": json.dumps(s)
                    }
                    sent_task_ids.add(s["task_id"])

                if all(s["status"] == "success" for s in statuses) and len(statuses) > 0:
                    if "done-all" not in sent_task_ids:
                        yield {
                            "id": "done-all",
                            "event": "music_done_all",
                            "data": json.dumps(statuses)
                        }
                        sent_task_ids.add("done-all")
                    break

            except Exception as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": "Database query failed", "detail": str(e)})
                }
                break

            await asyncio.sleep(polling_interval)

    return EventSourceResponse(event_generator(), ping=15)


@router.post(
    "/lanterns",
    response_model=ResponseModel[dict],
    responses={
        200: success_200_create_lantern,
        400: error_400_lantern_examples,
        500: error_500
    }
)
async def create_lanterns(
    request: Request,
    name: str = Form(..., min_length=1, max_length=50, description="사용자 이름 (1~50자)"),
    images: List[UploadFile] = File(..., description="이미지 파일 (jpg, jpeg, png, webp, 각 5MB 이하, 총 3장)"),
    is_public: bool = Form(True, description="랜턴을 공개할지 여부"),
):
    db = get_mongo_client(request)
    validate_name(name)
    validate_images(images)

    lantern_service = LanternService(db)
    lantern_id = await lantern_service.create_lanterns(
        name=name,
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
    request: Request,
    current_lantern_id: Optional[str] = Query(
        None,
        description="현재 체험 중인 사용자 랜턴 ID",
        regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"
    )
):
    db = get_mongo_client(request)
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
    request: Request,
    lantern_id: str = Path(
        ...,
        description="조회할 랜턴의 ID",
        regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"
    )
):
    db = get_mongo_client(request)
    lantern_service = LanternService(db)
    lantern = await lantern_service.get_lantern_detail(lantern_id)
    return success_response(
        data=lantern.model_dump(),
        message="Lantern detail"
    )
