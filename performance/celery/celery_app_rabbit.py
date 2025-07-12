import os
import sys
from celery import Celery
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from task_stub import long_dummy_task

broker_url = os.getenv("RABBITMQ_BROKER_URL")

celery = Celery(
    "worker_rabbit",
    broker=broker_url,
    backend=None  # RabbitMQ는 backend 없이도 동작 가능
)

@celery.task
def celery_task_rabbit(task_id):
    long_dummy_task(task_id)
    return {"task_id": task_id, "status": "done"}
