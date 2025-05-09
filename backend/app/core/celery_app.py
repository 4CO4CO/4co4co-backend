from celery import Celery

celery_app = Celery(
    "backend",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)

from app.core.tasks import panorama_tasks
from app.core.config import settings