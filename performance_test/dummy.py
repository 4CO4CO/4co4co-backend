import os
import random
import string
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# 환경 변수 (모두 반드시 존재해야 함)
MONGO_URI = os.environ["MONGO_URI"]
DB_NAME = os.environ["MONGO_DB_NAME"]
COLLECTION_NAME = os.environ["MONGO_COLLECTION_NAME"]
DUMMY_DATA_COUNT = int(os.environ["DUMMY_DATA_COUNT"])
DEFAULT_USER_NAME = os.environ["DEFAULT_USER_NAME"]

# Mongo 연결
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# 기존 데이터 삭제
collection.delete_many({})

# 랜덤 ID 생성 함수
def random_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# 더미 데이터 생성
for i in range(DUMMY_DATA_COUNT):
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
        "lantern_id": f"{DEFAULT_USER_NAME}-{i+1000}",
        "user_name": DEFAULT_USER_NAME,
        "images": images,
        "musics": [],
        "music_tasks": tasks,
        "music_statuses": statuses,
        "is_public": True,
        "created_at": datetime.utcnow()
    }

    collection.insert_one(lantern)

print(f"✅ {DUMMY_DATA_COUNT}개 더미 데이터 생성 완료!")
