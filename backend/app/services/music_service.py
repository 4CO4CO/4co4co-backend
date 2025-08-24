from datetime import datetime

import httpx

from app.core.config.settings import settings
from app.core.exceptions.types import AppError, NotFoundError
from app.repositories.lantern_repository import LanternRepository
from app.schemas.db.lantern import MusicInfo
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


def call_ai_server(
    image: str,
) -> str:
    """
    AI 서버에 단일 이미지 키와 설명을 보내고,
    성공 시 data.s3_key를 반환합니다.
    실패 시 AppError로 처리합니다.
    """
    url = f"{settings.AI_SERVER_URL}{settings.API_PREFIX}/generate-music"
    payload = {"image": image}

    try:
        logger.info(f"[AI Server] Request: url={url}, image={image}")
        resp = httpx.post(url, json=payload, timeout=1000.0)
        resp.raise_for_status()
        body = resp.json()
        logger.info(f"[AI Server] Response: status_code={resp.status_code}, body={body}")
    except Exception as e:
        logger.error(f"[AI Server] Request failed: {e}", exc_info=True)
        raise AppError(f"AI server request failed: {e}")

    if body.get("status") != "success":
        logger.error(f"[AI Server] Returned error: {body.get('message', 'unknown')}")
        raise AppError(f"AI returned error: {body.get('message', 'unknown')}")

    s3_key = body.get("data", {}).get("s3_key")
    if not s3_key or not isinstance(s3_key, str):
        logger.error("[AI Server] Invalid s3_key in response")
        raise AppError("AI server did not return a valid s3_key")

    logger.info(f"[AI Server] Music generated successfully: s3_key={s3_key}")
    return s3_key


class MusicService:
    def __init__(self, db):
        self.db = db
        self.lantern_repo = LanternRepository(db)

    def generate_music(
        self,
        lantern_id: str,
        image: str,
    ) -> str:
        """
        lantern_id에 해당하는 Lantern가 존재하는지 확인한 뒤,
        단일 image 키를 AI 서버에 보내 음악을 생성하고
        반환된 s3_key를 DB에 저장하고 리턴합니다.
        """
        logger.info(f"[MusicService] Generate music start: lantern_id={lantern_id}, image={image}")

        # 1) Lantern 존재 확인 (동기)
        lantern = self.lantern_repo.collection.find_one({"lantern_id": lantern_id})
        if not lantern:
            logger.warning(f"[MusicService] Lantern not found: {lantern_id}")
            raise NotFoundError(f"Lantern ID {lantern_id} not found.")

        # 2) AI 서버 호출
        s3_key = call_ai_server(image)

        # 3) MusicInfo 모델로 문서 생성
        music_info = MusicInfo(
            s3_path=s3_key,
            created_at=datetime.utcnow()
        ).model_dump(exclude={"id"})

        # 4) DB 업데이트: musics 배열에 푸시
        self.lantern_repo.collection.update_one(
            {"lantern_id": lantern_id},
            {"$push": {"musics": music_info}}
        )

        logger.info(f"[MusicService] Music info saved: lantern_id={lantern_id}, s3_key={s3_key}")
        return s3_key