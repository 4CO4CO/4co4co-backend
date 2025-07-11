from fastapi import FastAPI
import sqlite3
from datetime import datetime

app = FastAPI()

DB_PATH = "polling_tasks.db"

# DB 초기화
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()
task_counter = 0

@app.post("/polling")
def save_task():
    global task_counter
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task_id, status, created_at) VALUES (?, ?, ?)",
              (task_counter, "waiting", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    task_counter += 1
    return {"msg": f"Task {task_counter - 1} saved to DB"}