import json
import time
from datetime import datetime

import redis
import requests

from app.core.tasks.celery_app import celery_app
from app.core.config.settings import settings
from app.core.db.database import get_mongo_sync_client
from app.schemas.db.panorama import PanoramaDBModel

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)


def publish_status(lantern_id: str, status: str, step: str, extra: dict = None):
    message = {
        "lantern_id": lantern_id,
        "status": status,
        "step": step,
        "timestamp": datetime.utcnow().isoformat()
    }
    if extra:
        message.update(extra)
    redis_client.publish("lantern_updates", json.dumps(message))
    print(f"[Redis] Published update: {message}")


@celery_app.task
def generate_panorama_task(prompt, lantern_id, image_path):
    publish_status(lantern_id, "started", "Task started")

    if True:
        publish_status(lantern_id, "processing", "Mock processing panorama")
        print(f"[MOCK] Sleeping for 3 seconds to simulate processing...")
        time.sleep(3)
        panorama_path = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/panorama/mock-panorama.png"

    else:
        publish_status(lantern_id, "processing", "Sending image to AI server")
        try:
            with open(image_path, "rb") as img_file:
                ai_server_url = settings.AI_SERVER_URL + "/outpaint"
                response = requests.post(
                    ai_server_url,
                    files={"image": img_file},
                    data={"prompt": prompt}
                )
            response.raise_for_status()
            result = response.json()
            panorama_path = result["output_path"]
        except Exception as e:
            publish_status(lantern_id, "failed", "Error during AI processing", {"error": str(e)})
            raise

    publish_status(lantern_id, "saving_db", "Saving result to MongoDB")
    try:
        mongo_client = get_mongo_sync_client()
        panorama_collection = mongo_client["panorama"]
        panorama_doc = PanoramaDBModel(
            lantern_id=lantern_id,
            s3_path=panorama_path,
            created_at=datetime.utcnow()
        )
        insert_result = panorama_collection.insert_one(panorama_doc.model_dump(by_alias=True, exclude={"id"}))
        print(f"[DB] Inserted panorama document with ID: {insert_result.inserted_id}")

    except Exception as e:
        publish_status(lantern_id, "failed", "Error saving to MongoDB", {"error": str(e)})
        raise

    publish_status(lantern_id, "completed", "All done", {"s3_url": panorama_path})
    return {"message": "Panorama generated and saved", "s3_url": panorama_path}
