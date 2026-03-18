from celery import Celery
from app.core.config.settings import settings

celery_app = Celery(
    "backend",
    broker=settings.REDIS_URL, # 브로커: RabbitMQ -> Redis로 수정
    backend=settings.MONGO_URI, # 결과 저장소
    include=["app.core.tasks.music_tasks"],
)

celery_app.conf.update(
    task_default_queue='celery',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,

    # 작업이 성공적으로 끝났을 때만 ACK를 보내게 하기 위함 -> 불안정한 AI 서버를 대비해 메시지 유실 방지
    task_acks_late=True,

    # Redis 브로커 상세 설정
    broker_transport_options={
        # AI 작업이 넉넉히 끝날 수 있도록 대기 시간 설정
        'visibility_timeout': 3600,

        # Redis 연결이 끊겼을 때 재시도 설정
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.5,
        'interval_max': 3,
    },

    # 작업 자체에 대한 타임아웃 (태스크가 무한 루프 도는 것 방지)
    task_time_limit=1200,
    task_soft_time_limit=1000,
)