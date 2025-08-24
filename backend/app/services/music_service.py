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
    Call the AI server with a single image key to generate music.
    - Sends a POST request with {"image": image}
    - Returns the generated s3_key on success
    - Raises AppError on failure (request error or invalid response)
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

    # Validate response
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
    """
    Service layer for music generation.
    - Validates lantern existence
    - Calls AI server to generate music
    - Saves generated music metadata into the lantern document
    """

    def __init__(self, db):
        self.db = db
        self.lantern_repo = LanternRepository(db)

    def generate_music(
        self,
        lantern_id: str,
        image: str,
    ) -> str:
        """
        Generate background music for a given lantern and image.
        Workflow:
        1. Validate lantern existence in DB
        2. Call AI server with the image key
        3. Create a MusicInfo entry
        4. Push the music metadata into the lantern document
        Returns:
            str: s3_key of the generated music file
        """
        logger.info(f"[MusicService] Generate music start: lantern_id={lantern_id}, image={image}")

        # 1) Ensure lantern exists
        lantern = self.lantern_repo.collection.find_one({"lantern_id": lantern_id})
        if not lantern:
            logger.warning(f"[MusicService] Lantern not found: {lantern_id}")
            raise NotFoundError(f"Lantern ID {lantern_id} not found.")

        # 2) Call AI server
        s3_key = call_ai_server(image)

        # 3) Build MusicInfo document
        music_info = MusicInfo(
            s3_path=s3_key,
            created_at=datetime.utcnow()
        ).model_dump(exclude={"id"})

        # 4) Update DB: append new music entry
        self.lantern_repo.collection.update_one(
            {"lantern_id": lantern_id},
            {"$push": {"musics": music_info}}
        )

        logger.info(f"[MusicService] Music info saved: lantern_id={lantern_id}, s3_key={s3_key}")
        return s3_key