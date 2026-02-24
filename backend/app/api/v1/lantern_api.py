import asyncio
import json
import time
from typing import Optional, List, Set, Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, Query, Path, Request, Header
from sse_starlette.sse import EventSourceResponse

from app.core.config.settings import settings
from app.core.db.database import get_mongo_client
from app.core.exceptions.types import NotFoundError
from app.core.logging.logger import get_logger
from app.core.response.response import success_response, success_no_cache_response
from app.core.validation.lantern_validation import validate_name, validate_images
from app.repositories.lantern_repository import LanternRepository
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel
from app.schemas.response.schemas import ResponseModel
from app.schemas.swagger import (
    error_400, error_404, error_500,
    error_400_lantern_examples, success_200_create_lantern
)
from app.services.lantern_service import LanternService

logger = get_logger(__name__)
router = APIRouter()


# --- Helper Functions for SSE ---

def get_initial_sent_tasks(doc: Dict[str, Any], resume: bool, last_event_id: Optional[str]) -> Set[str]:
    """
    using last_event_id to preventing duplication
    """
    sent_task_ids = set()
    if resume and last_event_id:
        statuses = doc.get("music_statuses", [])
        for s in statuses:
            sent_task_ids.add(s["task_id"])
            if s["task_id"] == last_event_id:
                break
    return sent_task_ids


def get_new_status_updates(statuses: List[Dict[str, Any]], sent_task_ids: Set[str]) -> List[Dict[str, Any]]:
    """
    filtering pending status -> returns success & failed
    """
    return [
        s for s in statuses
        if s["status"] in ["success", "failed"] and s["task_id"] not in sent_task_ids
    ]


def format_sse_event(status_data: Dict[str, Any]) -> Dict[str, str]:
    """
    formating(DB -> SSE)
    """
    event_name = "music_done_partial" if status_data["status"] == "success" else "music_failed"
    return {
        "id": status_data["task_id"],
        "event": event_name,
        "data": json.dumps(status_data)
    }


# --- Router Endpoints ---

@router.get("/lanterns/{lantern_id}/music-status")
async def music_status(
        request: Request,
        lantern_id: str = Path(..., regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$"),
        resume: bool = Query(False),
        last_event_id: str = Header(None, convert_underscores=False)
):
    db = get_mongo_client(request)
    repo = LanternRepository(db)

    # connection redis
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis.pubsub()

    await pubsub.subscribe(f"lantern_music:{lantern_id}")

    start_time = time.time()

    # check db
    doc = await repo.find_by_lantern_id(lantern_id)
    if not doc:
        await pubsub.unsubscribe()
        raise NotFoundError(f"Lantern ID '{lantern_id}' not found")

    # filter sent task with last-event-id
    sent_task_ids = get_initial_sent_tasks(doc, resume, last_event_id)

    async def event_generator():
        try:
            # sent task is already marked as success/failed
            initial_statuses = doc.get("music_statuses", [])
            new_updates = get_new_status_updates(initial_statuses, sent_task_ids)
            for s in new_updates:
                yield format_sse_event(s)
                sent_task_ids.add(s["task_id"])

            while True:
                if await request.is_disconnected(): break
                if time.time() - start_time > settings.SSE_TIMEOUT: break

                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message:
                    data = json.loads(message['data'])
                    if data["task_id"] not in sent_task_ids:
                        yield format_sse_event(data)
                        sent_task_ids.add(data["task_id"])

                # DB check to ensure all tasks are truly finished
                current_doc = await repo.find_by_lantern_id(lantern_id)
                statuses = current_doc.get("music_statuses", [])

                if all(s["status"] in ["success", "failed"] for s in statuses) and len(statuses) > 0:
                    if "done-all" not in sent_task_ids:
                        yield {
                            "id": "done-all",
                            "event": "music_done_all",
                            "data": json.dumps(statuses)
                        }
                    break

        finally:
            await pubsub.unsubscribe(f"lantern_music:{lantern_id}")
            await redis.close()

    return EventSourceResponse(event_generator(), ping=15)


@router.post(
    "/lanterns",
    response_model=ResponseModel[dict],
    responses={200: success_200_create_lantern, 400: error_400_lantern_examples, 500: error_500}
)
async def create_lanterns(
        request: Request,
        name: str = Form(..., min_length=1, max_length=50, description="User name"),
        images: List[UploadFile] = File(..., description="Image files"),
        is_public: bool = Form(True, description="Public visibility"),
):
    """
    create a new lantern(needs user's info & image metadata)
    """
    logger.info(f"[create_lanterns] Request received: name={name}")

    db = get_mongo_client(request)
    validate_name(name)
    validate_images(images)

    lantern_service = LanternService(db)
    lantern_id = await lantern_service.create_lanterns(
        name=name, images=images, is_public=is_public
    )

    logger.info(f"[create_lanterns] Lantern created: {lantern_id}")
    return success_response(data={"lantern_id": lantern_id}, message="Lantern Created")


@router.get(
    "/lanterns",
    response_model=ResponseModel[List[LanternResponseModel]],
    responses={200: {"description": "Lantern List"}, 400: error_400, 404: error_404, 500: error_500}
)
async def get_lantern_list(
        request: Request,
        current_lantern_id: Optional[str] = Query(None, regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$")
):
    """
    list of recent lanterns + excluding or highlighting the current user's lantern
    """
    db = get_mongo_client(request)
    lantern_service = LanternService(db)
    lanterns = await lantern_service.get_recent_lanterns(current_lantern_id=current_lantern_id)

    return success_no_cache_response(
        data=[lantern.model_dump() for lantern in lanterns],
        message="Lantern list"
    )


@router.get(
    "/lanterns/{lantern_id}",
    response_model=ResponseModel[LanternDetailResponseModel],
    responses={200: {"description": "Lantern Detail"}, 404: error_404}
)
async def get_lantern_detail(
        request: Request,
        lantern_id: str = Path(..., regex=r"^[가-힣a-zA-Z0-9]+-[0-9]{4}$")
):
    """
    for detailed info for specific lantern
    """
    db = get_mongo_client(request)
    lantern_service = LanternService(db)
    lantern = await lantern_service.get_lantern_detail(lantern_id)

    return success_response(data=lantern.model_dump(), message="Lantern detail")