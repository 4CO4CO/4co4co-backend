from app.core.db.database import get_db
from app.core.tasks.celery_app import celery_app
from app.services.music_service import MusicService


@celery_app.task(name="process_lantern_music")
def process_lantern_music(
    lantern_id: str,
    image_key: str,
    description: str
) -> str:
    """
    Celery 워커가 실행할 태스크.
    image_key 하나에 대해 MusicService.generate_music을 호출하고,
    생성된 s3_key를 반환합니다.
    """
    db = get_db()
    service = MusicService(db)

    s3_key = service.generate_music(
        lantern_id=lantern_id,
        image=image_key,
        description=description,
    )
    return s3_key
