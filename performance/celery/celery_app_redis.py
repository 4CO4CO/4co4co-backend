import os
import sys
from celery import Celery
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from task_stub import long_dummy_task

broker_url = os.getenv("REDIS_BROKER_URL")
backend_url = os.getenv("REDIS_BACKEND_URL")

celery = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url
)

@celery.task
def celery_task(task_id):
    long_dummy_task(task_id)
    return {"task_id": task_id, "status": "done"}