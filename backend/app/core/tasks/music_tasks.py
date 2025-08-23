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
    Celery 워커가 실행할 태스크.
    image_key 하나에 대해 MusicService.generate_music을 호출하고,
    생성된 s3_key를 반환하고, DB에 상태를 'success'로 업데이트합니다.
    """
    try:
        logger.info(f"Starting music generation task for lantern_id={lantern_id}, image_key={image_key}")
        db = get_db()
        service = MusicService(db)

        # 음악 생성
        s3_key = service.generate_music(
            lantern_id=lantern_id,
            image=image_key,
        )

        # 상태 업데이트: 'success'
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

        logger.info(f"Music generated successfully for image_key={image_key}, s3_key={s3_key}")
        return s3_key

    except Exception as e:
        logger.error(f"Music generation task failed for lantern_id={lantern_id}, image_key={image_key}: {e}", exc_info=True)

        # 상태 업데이트: 'failed'
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
            logger.warning(f"Failed to update task failure status for image_key={image_key}: {update_error}")

        raise e
