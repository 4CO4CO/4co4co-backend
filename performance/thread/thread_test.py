from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor
from task_stub import long_dummy_task

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=5)
task_counter = 0

@app.post("/thread")
def thread_task():
    global task_counter
    task_id = task_counter
    task_counter += 1
    executor.submit(long_dummy_task, task_id)
    return {"msg": f"Thread task {task_id} submitted"}