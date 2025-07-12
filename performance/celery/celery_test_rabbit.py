from fastapi import FastAPI
from celery_app_rabbit import celery_task_rabbit

app = FastAPI()
task_counter = 0

@app.post("/celery")
def run_celery_task():
    global task_counter
    task_id = task_counter
    task_counter += 1
    celery_task_rabbit.delay(task_id)
    return {"msg": f"RabbitMQ Celery task {task_id} submitted"}
