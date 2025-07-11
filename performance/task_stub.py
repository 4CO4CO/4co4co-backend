import time

def long_dummy_task(task_id: int):
    start = time.time()
    print(f"[{task_id}] 작업 시작")
    time.sleep(5)  # 실제 AI 모델 대신 대기
    end = time.time()
    print(f"[{task_id}] 작업 완료 (소요: {round(end - start, 2)}초)")
