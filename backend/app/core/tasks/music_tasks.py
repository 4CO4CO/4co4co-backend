import time

from app.core.db.database import get_db
from app.core.logging.logger import get_logger
from app.core.tasks.celery_app import celery_app
from app.repositories.lantern_repository import LanternRepository
from app.services.music_service import MusicService

logger = get_logger(__name__)


@celery_app.task(
    name="process_lantern_music",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def process_lantern_music(
    lantern_id: str,
    image_key: str,
) -> str:
    """
    Celery worker task for generating music from a single image key.

    Workflow:
    1. Create a MusicService instance with a DB connection
    2. Call MusicService.generate_music() to generate background music
    3. Update the corresponding lantern document in MongoDB:
       - Set status to "success"
       - Save the generated s3_key
    4. Return the generated s3_key

    On failure:
    - Logs the error
    - Updates the status of the lantern document to "failed"
    - Retries up to the configured number of times
    """
    start_time = time.time()
    try:
        logger.info(f"[Task Start] lantern_id={lantern_id}, image_key={image_key}")
        db = get_db()
        service = MusicService(db)

        # Generate music for the given image
        s3_key = service.generate_music(
            lantern_id=lantern_id,
            image=image_key,
        )

        # Update DB status to "success"
        repo = LanternRepository(db)
        repo.collection.update_one(
            {"lantern_id": lantern_id, "music_statuses.image_s3": image_key},
            {
                "$set": {
                    "music_statuses.$.status": "success",
                    "music_statuses.$.s3_key": s3_key
                }
            }
        )

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"[Task Success] image_key={image_key}, s3_key={s3_key}, elapsed={elapsed}s")
        return s3_key

    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        logger.error(
            f"[Task Failed] lantern_id={lantern_id}, image_key={image_key}, elapsed={elapsed}s, error={e}",
            exc_info=True
        )

        # Update DB status to "failed"
        try:
            db = get_db()
            repo = LanternRepository(db)
            repo.collection.update_one(
                {"lantern_id": lantern_id, "music_statuses.image_s3": image_key},
                {
                    "$set": {
                        "music_statuses.$.status": "failed"
                    }
                }
            )
        except Exception as update_error:
            logger.warning(
                f"[Task Update Failed] image_key={image_key}, update_error={update_error}"
            )

        raise e
