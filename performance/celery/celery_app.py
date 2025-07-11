import os
import sys

from celery import Celery

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from task_stub import long_dummy_task

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0",   # Redis가 실행 중이어야 함
    backend="redis://localhost:6379/0"
)

@celery.task
def celery_task(task_id):
    long_dummy_task(task_id)
    return {"task_id": task_id, "status": "done"}
