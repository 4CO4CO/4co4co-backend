import sqlite3
import time
import sys
import os

# task_stub 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from task_stub import long_dummy_task

DB_PATH = "polling_tasks.db"


def polling_worker(interval=2):
    print("개선된 Polling 워커 실행 시작...")
    while True:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 먼저 waiting 상태에서 5개 추출
        c.execute("SELECT id, task_id FROM tasks WHERE status = 'waiting' LIMIT 5")
        tasks = c.fetchall()

        for db_id, task_id in tasks:
            # 처리권한 확보 시도
            c.execute("UPDATE tasks SET status = 'processing' WHERE id = ? AND status = 'waiting'", (db_id,))
            conn.commit()

            if c.rowcount == 1:
                print(f"[polling] task_id {task_id} 실행")
                long_dummy_task(task_id)
                c.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (db_id,))
                conn.commit()
            else:
                print(f"[polling] task_id {task_id} 이미 처리 중 또는 완료됨 (skip)")

        conn.close()
        time.sleep(interval)


if __name__ == "__main__":
    polling_worker(interval=2)
