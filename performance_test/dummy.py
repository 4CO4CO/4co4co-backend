import random
import string
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Mongo 연결
client = MongoClient("mongodb://localhost:27017")
db = client["memory"]
collection = db["lantern"]

# 컬렉션 초기화 (기존 문서 제거)
collection.delete_many({})

# 랜덤 ID 생성 함수
def random_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# 더미 문서 생성
for i in range(300):
    images = [
        {
            "s3_path": f"lanterns/pending_image_{i}_1.jpg",
            "original_filename": "tree.jpg",
            "file_extension": "jpg",
            "file_size": random.randint(90000, 110000),
        },
        {
            "s3_path": f"lanterns/pending_image_{i}_2.jpg",
            "original_filename": "flower.jpg",
            "file_extension": "jpg",
            "file_size": random.randint(90000, 110000),
        },
        {
            "s3_path": f"lanterns/pending_image_{i}_3.jpg",
            "original_filename": "sky.jpg",
            "file_extension": "jpg",
            "file_size": random.randint(90000, 110000),
        }
    ]

    tasks = []
    statuses = []
    for j in range(3):
        img_path = images[j]["s3_path"]
        task_id = f"{random_id()}-{111111 * (j+1)}"
        tasks.append({
            "task_id": task_id,
            "image_s3": img_path
        })
        statuses.append({
            "image_s3": img_path,
            "task_id": task_id,
            "status": random.choice(["success", "pending"]),
            "s3_key": f"lanterns/music_{i}_{chr(97+j)}.wav" if random.random() > 0.3 else None
        })

    lantern = {
        "_id": ObjectId(),
        "lantern_id": f"박유나-{i+1000}",  # → 숫자 4자리로 맞춤
        "user_name": "박유나",
        "images": images,
        "musics": [],
        "music_tasks": tasks,
        "music_statuses": statuses,
        "is_public": True,
        "created_at": datetime.utcnow()
    }

    collection.insert_one(lantern)

print("✅ 300개 더미 데이터 생성 완료!")
