import time
import json
import redis
from app.core.db.database import get_db
from app.core.logging.logger import get_logger
from app.core.tasks.celery_app import celery_app
from app.repositories.lantern_repository import LanternRepository
from app.services.music_service import MusicService
from app.core.config.settings import settings

logger = get_logger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@celery_app.task(
    name="process_lantern_music",
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=True, # 지수 백오프 적용 -> GPU 부족을 고려 -> 시간을 대기를 하고 재시도하기 위함
    retry_kwargs={"max_retries": 3}
)
def process_lantern_music(lantern_id: str, image_key: str):
    db = get_db()
    repo = LanternRepository(db)
    service = MusicService(db)

    # 이미 성공한 경우 -> AI 요청 안 보내기(acks_late=True -> 작업 중복 방지)
    existing_doc = repo.collection.find_one({
        "lantern_id": lantern_id,
        "music_statuses": {
            "$elemMatch": {"image_s3": image_key, "status": "success"}
        }
    }, {"music_statuses.$": 1})

    if existing_doc:
        logger.info(f"[Skip Task] Already succeeded: lantern_id={lantern_id}, image={image_key}")
        return existing_doc["music_statuses"][0].get("s3_key")

    try:
        logger.info(f"[Task Start] lantern_id={lantern_id}, image={image_key}")
        s3_key = service.generate_music(lantern_id=lantern_id, image=image_key) #AI 서버에 요청 보내기

        # DB 저장 -> Redis Pub (재접속을 통해 Redis 방송을 못 들었을 경우 대비)
        repo.collection.update_one(
            {"lantern_id": lantern_id, "music_statuses.image_s3": image_key},
            {
                "$set": {
                    "music_statuses.$.status": "success",
                    "music_statuses.$.s3_key": s3_key,
                    "music_statuses.$.updated_at": time.time()
                }
            }
        )

        # Redis Pub/Sub
        event_payload = {
            "lantern_id": lantern_id,
            "image_s3": image_key,
            "status": "success",
            "s3_key": s3_key,
            "task_id": image_key
        }
        redis_client.publish(f"lantern_music:{lantern_id}", json.dumps(event_payload))

        logger.info(f"[Task Success] lantern_id={lantern_id}, image={image_key}")
        return s3_key


    except Exception as e:

        logger.error(f"[Task Error] lantern_id={lantern_id}, error={e}")

        repo.collection.update_one(

            # DB 기록
            {"lantern_id": lantern_id, "music_statuses.image_s3": image_key},
            {
                "$set": {
                    "music_statuses.$.status": "failed",
                    "music_statuses.$.error_msg": str(e),
                    "music_statuses.$.updated_at": time.time()
                }
            }
        )

        # Redis 기록
        error_payload = {
            "lantern_id": lantern_id,
            "image_s3": image_key,
            "status": "failed",
            "task_id": image_key
        }
        redis_client.publish(f"lantern_music:{lantern_id}", json.dumps(error_payload))

        raise e