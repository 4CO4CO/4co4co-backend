import os
import time
import random

from dotenv import load_dotenv
from pymongo import MongoClient

# .env 로드
load_dotenv()

# 환경 변수 로드
MONGO_URI = os.environ["MONGO_URI"]
DB_NAME = os.environ["MONGO_DB_NAME"]
COLLECTION_NAME = os.environ["MONGO_COLLECTION_NAME"]
DEFAULT_USER_NAME = os.environ["DEFAULT_USER_NAME"]
DUMMY_DATA_COUNT = int(os.environ["DUMMY_DATA_COUNT"])
TEST_INDEX = True  # True면 인덱스 생성 후 측정

# Mongo 연결
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# 인덱스 생성 여부
if TEST_INDEX:
    print("\n인덱스 생성 중... (lantern_id)")
    collection.create_index("lantern_id", unique=True)
    print("인덱스 생성 완료\n")

# 무작위 100개 샘플 ID 생성
sample_ids = random.sample(range(1000, 1000 + DUMMY_DATA_COUNT), 100)
execution_times = []
stages = set()
doc_counts = []

print("쿼리 실행 성능 측정 중...\n")

for i in sample_ids:
    lantern_id = f"{DEFAULT_USER_NAME}-{i}"
    start = time.perf_counter()
    explain = collection.find({"lantern_id": lantern_id}).explain()
    end = time.perf_counter()

    execution_time = (end - start) * 1000  # ms
    execution_times.append(execution_time)

    try:
        stats = explain["executionStats"]
        doc_counts.append(stats.get("totalDocsExamined", -1))
    except:
        doc_counts.append(-1)

    stage = explain["queryPlanner"]["winningPlan"]["stage"]
    stages.add(stage)

# 결과 출력
print(f"[100건 테스트 결과]")
print(f"- 평균 응답 시간: {sum(execution_times)/len(execution_times):.2f}ms")
print(f"- 최소 응답 시간: {min(execution_times):.2f}ms")
print(f"- 최대 응답 시간: {max(execution_times):.2f}ms")
print(f"- 사용된 인덱스 단계: {', '.join(stages)}")
print(f"- 평균 문서 스캔 수: {sum(doc_counts)/len(doc_counts):.2f}개")

client.close()
