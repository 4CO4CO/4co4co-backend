from celery import Celery
from app.core.config.settings import settings

# Create a Celery application instance
celery_app = Celery(
    "backend",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"],  # 워커 태스크 위치 지정
)

# Update Celery configuration
celery_app.conf.update(
    task_default_queue='celery',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    task_acks_late=True,          # 작업 완료 후 ACK 전송
    worker_prefetch_multiplier=1, # 한 번에 하나의 작업만 가져옴 (AI 작업 부하 분산)
)