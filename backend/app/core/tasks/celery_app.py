from celery import Celery
from app.core.config.settings import settings

celery_app = Celery(
    "backend",
    broker=settings.REDIS_URL,
    backend=settings.MONGO_URI,
    include=["app.core.tasks.music_tasks"],
)

# configuration
celery_app.conf.update(
    task_default_queue='celery',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    task_acks_late=True,
)
