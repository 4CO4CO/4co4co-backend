import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    database = client[MONGO_DB]
except Exception as e:
    print(f"MongoDB 연결 실패: {e}")
