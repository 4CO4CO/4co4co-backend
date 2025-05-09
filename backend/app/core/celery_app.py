from celery import Celery

from app.core.config.settings import settings

celery_app = Celery(
    "backend",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)

import app.core.tasks.panorama_tasks

