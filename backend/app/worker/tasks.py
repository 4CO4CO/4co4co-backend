import time
import requests
from datetime import datetime
from celery import shared_task

from app.core.config.settings import settings
from app.core.logging.logger import get_logger
from app.core.db.database import get_mongo_sync_client

logger = get_logger(__name__)


def call_ai_server_sync(image_key: str) -> str:
    """
    Call the AI server synchronously using requests.
    """
    url = f"{settings.AI_SERVER_URL}{settings.API_PREFIX}/generate-music"
    payload = {"image_path": image_key}

    try:
        # Increase timeout to 600s (10 min) for heavy AI tasks
        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()
        body = response.json()

        if body.get("status") != "success":
            raise ValueError(f"AI Server Error: {body.get('message')}")

        s3_key = body.get("data", {}).get("s3_key")
        if not s3_key:
            raise ValueError("Invalid s3_key returned from AI Server")

        return s3_key

    except Exception as e:
        logger.error(f"[AI Sync Call Failed] {e}")
        raise e


@shared_task(
    name="process_lantern_music",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def process_lantern_music(lantern_id: str, image_key: str):
    """
    [Synchronous Celery Task]
    1. Connect to MongoDB (Sync)
    2. Call AI Server (Sync)
    3. Update MongoDB (Sync)
    """
    start_time = time.time()
    logger.info(f"[Task Start] lantern_id={lantern_id}, image={image_key}")

    # 1. DB Connection (Sync)
    db = get_mongo_sync_client()
    collection = db["lanterns"]

    try:
        # 2. Call AI Server
        s3_key = call_ai_server_sync(image_key)

        # 3. Update DB (Success)
        result = collection.update_one(
            {
                "lantern_id": lantern_id,
                "music_statuses.image_s3": image_key
            },
            {
                "$set": {
                    "music_statuses.$.status": "success",
                    "music_statuses.$.s3_key": s3_key,
                    "music_statuses.$.updated_at": datetime.utcnow()
                },
                "$push": {
                    "musics": {
                        "s3_path": s3_key,
                        "created_at": datetime.utcnow()
                    }
                }
            }
        )

        if result.modified_count == 0:
            logger.warning(f"[Task Warning] No document updated for {lantern_id}")

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"[Task Success] {lantern_id} / {s3_key} ({elapsed}s)")
        return s3_key

    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        logger.error(f"[Task Failed] {lantern_id} ({elapsed}s) - {e}", exc_info=True)

        # 4. Update DB (Failed)
        try:
            collection.update_one(
                {
                    "lantern_id": lantern_id,
                    "music_statuses.image_s3": image_key
                },
                {
                    "$set": {
                        "music_statuses.$.status": "failed",
                        "music_statuses.$.error_msg": str(e),
                        "music_statuses.$.updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as db_err:
            logger.error(f"[Task DB Error] Failed to update error status: {db_err}")

        raise e
