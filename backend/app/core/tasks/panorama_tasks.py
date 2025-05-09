import json
import time
from datetime import datetime

import redis
import requests

from app.core.celery_app import celery_app
from app.core.config.settings import settings
from app.core.db.database import get_mongo_sync_client
from app.schemas.db.panorama import PanoramaDBModel

redis_client = redis.Redis(host='localhost', port=6379, db=0)


@celery_app.task
def generate_panorama_task(prompt, lantern_id, image_path):
    if settings.USE_MOCK:
        print(f"[MOCK] Sleeping for 3 seconds to simulate processing...")
        time.sleep(3)
        panorama_path = f"mock_output/outpainted_{image_path.split('/')[-1]}"
    else:
        with open(image_path, "rb") as img_file:
            response = requests.post(
                "http://localhost:8001/api/v1/outpaint",
                files={"image": img_file},
                data={"prompt": prompt}
            )
        response.raise_for_status()
        result = response.json()
        panorama_path = result["output_path"]

    s3_path = f"https://s3.bucket/{panorama_path}"

    # MongoDB 저장
    mongo_client = get_mongo_sync_client()
    panorama_collection = mongo_client["panorama"]
    panorama_doc = PanoramaDBModel(
        lantern_id=lantern_id,
        s3_path=s3_path,
        created_at=datetime.utcnow()
    )
    insert_result = panorama_collection.insert_one(panorama_doc.model_dump(by_alias=True, exclude={"id"}))
    print(f"[DB] Inserted panorama document with ID: {insert_result.inserted_id}")

    # Redis Pub/Sub: 작업 완료 이벤트 발행
    redis_message = json.dumps({
        "lantern_id": lantern_id,
        "status": "completed",
        "s3_url": s3_path
    })
    redis_client.publish("lantern_updates", redis_message)
    print(f"[Redis] Published update for lantern_id: {lantern_id}")

    return {"message": "Panorama generated and saved", "s3_url": s3_path}
