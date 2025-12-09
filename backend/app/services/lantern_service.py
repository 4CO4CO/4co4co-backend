import json
import random
from datetime import datetime
from typing import List, Tuple, Optional

import redis.asyncio as redis
from fastapi import UploadFile, Request

from app.core.config.s3 import upload_file_to_s3, generate_presigned_url
from app.core.config.settings import settings
from app.core.exceptions.types import FileSaveError, NotFoundError, ValidationError
from app.core.logging.logger import get_logger
from app.repositories.lantern_repository import LanternRepository
from app.schemas.db.lantern import LanternDBModel, ImageInfo, MusicStatusInfo
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel

logger = get_logger(__name__)

redis_async_client = redis.from_url(settings.CELERY_BROKER_URL)

def to_lantern_model(doc: dict, current_lantern_id: Optional[str]) -> LanternResponseModel:
    """Helper to convert DB doc to ResponseModel"""
    return LanternResponseModel(
        lantern_id=doc["lantern_id"],
        owner_name=doc["user_name"],
        is_current_lantern=(doc["lantern_id"] == current_lantern_id),
    )


class LanternService:
    def __init__(self, db):
        self.lantern_repo = LanternRepository(db)

    # -------------------------------
    # Create (Metadata Only)
    # -------------------------------
    async def create_lantern_metadata(
            self,
            name: str,
            images: List[UploadFile],
            is_public: bool = True,
    ) -> Tuple[str, List[ImageInfo]]:
        """
        1. Generate unique ID
        2. Upload images to S3
        3. Save metadata to DB with 'pending' status
        4. Return lantern_id and image info for Task triggering
        """
        logger.info(f"[LanternService] Creating metadata for user={name}")

        # 1. Generate unique lantern_id
        lantern_id = await self._generate_unique_id(name)

        # 2. Upload images to S3
        uploaded_images: List[ImageInfo] = []
        for img in images:
            path, orig, ext, size = await self._upload_image_to_s3(img)
            uploaded_images.append(
                ImageInfo(
                    s3_key=path,
                    original_filename=orig,
                    file_extension=ext,
                    file_size=size,
                )
            )

        # 3. Init music status (Pending)
        music_statuses: List[MusicStatusInfo] = [
            MusicStatusInfo(
                image_s3=info.s3_key,
                task_id="",
                status="pending",
                s3_key=None,
            )
            for info in uploaded_images
        ]

        # 4. Insert lantern doc
        lantern_doc = LanternDBModel(
            lantern_id=lantern_id,
            user_name=name,
            images=uploaded_images,
            musics=[],
            music_tasks=[],
            music_statuses=music_statuses,
            is_public=is_public,
            created_at=datetime.utcnow(),
        )

        await self.lantern_repo.insert_lantern(
            lantern_doc.model_dump(exclude={"id"})
        )

        logger.info(f"[LanternService] Metadata saved: {lantern_id}")
        return lantern_id, uploaded_images

    # -------------------------------
    # SSE Logic
    # -------------------------------
    async def subscribe_music_status(
            self, request: Request, lantern_id: str, resume: bool, last_event_id: str = None
    ):
        """
        [Redis Pub/Sub 방식]
        1. 먼저 DB를 한 번 조회해서 이미 완료된 게 있는지 확인 (새로고침 대비)
        2. 그 후 Redis 채널을 구독하여 실시간 이벤트를 기다림
        """

        # 이미 완료된 작업이 있는지 DB 조회
        doc = await self.lantern_repo.find_by_lantern_id(lantern_id)
        if not doc:
            yield {"event": "error", "data": json.dumps({"error": "Lantern not found"})}
            return

        # 이미 성공/실패한 작업들을 먼저 보내줌 (새로고침 시 빈 화면 방지)
        statuses = doc.get("music_statuses", [])
        completed_count = 0
        for s in statuses:
            if s["status"] in ["success", "failed"]:
                completed_count += 1
                yield {
                    "event": "music_done_partial" if s["status"] == "success" else "music_failed",
                    "data": json.dumps(s, default=str)
                }

        # 모든 작업이 이미 끝났으면 Redis 연결할 필요 없이 종료
        if completed_count == len(statuses) and statuses:
            yield {"event": "music_done_all", "data": json.dumps(statuses, default=str)}
            return

        # 2. Redis Pub/Sub 시작
        pubsub = redis_async_client.pubsub()
        channel_name = f"lantern_status:{lantern_id}"
        await pubsub.subscribe(channel_name)

        logger.info(f"[SSE] Subscribed to Redis channel: {channel_name}")

        try:
            # Redis 메시지 루프
            async for message in pubsub.listen():
                if await request.is_disconnected():
                    logger.info(f"[SSE] Client disconnected: {lantern_id}")
                    break

                if message["type"] == "message":
                    raw_data = message["data"]
                    payload = json.loads(raw_data)

                    status = payload["status"]

                    # 이벤트 타입 결정
                    event_type = "music_progress"  # processing, retrying
                    if status == "success":
                        event_type = "music_done_partial"
                    elif status == "failed":
                        event_type = "music_failed"

                    yield {
                        "event": event_type,
                        "data": raw_data  # 그대로 전송
                    }

        except Exception as e:
            logger.error(f"[SSE] PubSub Error: {e}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
        finally:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()

    # -------------------------------
    # Read Operations
    # -------------------------------
    async def get_recent_lanterns(
            self, current_lantern_id: Optional[str] = None, limit: int = 20
    ):
        current_doc = None
        if current_lantern_id:
            current_doc = await self.get_lantern_detail_raw(current_lantern_id)
            limit -= 1

        other_docs = await self.lantern_repo.find_random_lanterns(
            exclude_lantern_id=current_lantern_id if current_doc else None, limit=limit
        )

        docs = [current_doc] + other_docs if current_doc else other_docs
        return [to_lantern_model(doc, current_lantern_id) for doc in docs if doc]

    async def get_lantern_detail(self, lantern_id: str):
        """Fetch detail with presigned URLs"""
        lantern = await self.get_lantern_detail_raw(lantern_id)

        # Convert to Presigned URLs
        images = []
        for image in lantern.get("images", []):
            s3_key = image.get("s3_key")
            if s3_key:
                url = await generate_presigned_url(s3_key)
                if url: images.append(url)

        musics = []
        for music in lantern.get("musics", []):
            s3_path = music.get("s3_path")
            if s3_path:
                url = await generate_presigned_url(s3_path)
                if url: musics.append(url)

        return LanternDetailResponseModel(
            lantern_id=lantern["lantern_id"],
            owner_name=lantern["user_name"],
            images=images,
            background_sounds=musics,
        )

    async def get_lantern_detail_raw(self, lantern_id: str) -> dict:
        lantern = await self.lantern_repo.find_by_lantern_id(lantern_id)
        if not lantern:
            raise NotFoundError(message=f"Lantern ID {lantern_id} not found.")
        return lantern

    # -------------------------------
    # Helpers
    # -------------------------------
    async def _generate_unique_id(self, name: str) -> str:
        for _ in range(5):
            code = str(random.randint(1000, 9999))
            lantern_id = f"{name}-{code}"
            if not await self.lantern_repo.exists_by_lantern_id(lantern_id):
                return lantern_id
        raise ValidationError("Duplicate lantern ID")

    @staticmethod
    async def _upload_image_to_s3(image: UploadFile):
        original_filename = image.filename
        file_extension = original_filename.split(".")[-1]
        try:
            s3_key, file_size = await upload_file_to_s3(image, folder="lanterns")
            if s3_key is None:
                raise FileSaveError("S3 upload failed")
            return s3_key, original_filename, file_extension, file_size
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise FileSaveError(f"File upload failed: {e}") from e