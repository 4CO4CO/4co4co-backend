from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions.types import DatabaseError
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class LanternRepository:
    """
    Repository class for interacting with the 'lanterns' collection in MongoDB.
    Provides CRUD-like methods with error handling using custom DatabaseError.
    Async implementation for FastAPI.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["lanterns"]

    async def insert_lantern(self, user_doc: dict) -> str:
        """
        Insert a new lantern document into the collection.
        Returns:
            str: The inserted document's ID (lantern_id)
        """
        try:
            await self.collection.insert_one(user_doc)
            return user_doc.get("lantern_id")
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_by_lantern_id(self, lantern_id: str) -> Optional[dict]:
        """
        Find a lantern document by its lantern_id.
        """
        try:
            return await self.collection.find_one({"lantern_id": lantern_id})
        except Exception as e:
            raise DatabaseError(f"find_by_lantern_id failed for {lantern_id}: {e}") from e

    async def count_documents(self, filter_dict: dict) -> int:
        """
        Count documents in the collection matching the given filter.
        """
        try:
            return await self.collection.count_documents(filter_dict)
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def exists_by_lantern_id(self, lantern_id: str) -> bool:
        """
        Check if a lantern with the given lantern_id exists.
        """
        try:
            document = await self.collection.find_one({"lantern_id": lantern_id}, {"_id": 1})
            return document is not None
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_random_lanterns(self, limit: int = 20, exclude_lantern_id: Optional[str] = None) -> List[dict]:
        """
        Retrieve random lantern documents that are public.
        """
        try:
            match_stage = {"is_public": True}
            if exclude_lantern_id:
                match_stage["lantern_id"] = {"$ne": exclude_lantern_id}

            pipeline = [
                {"$match": match_stage},
                {"$sample": {"size": limit}}
            ]
            cursor = self.collection.aggregate(pipeline)
            return [doc async for doc in cursor]
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def update_music_task(self, lantern_id: str, image_key: str, task_id: str) -> bool:
        """
        Update the task_id for a given image in the music_statuses array.
        """
        try:
            result = await self.collection.update_one(
                {"lantern_id": lantern_id, "music_statuses.image_s3": image_key},
                {"$set": {"music_statuses.$.task_id": task_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(
                f"update_music_task failed for lantern_id={lantern_id}, image_key={image_key}: {e}"
            ) from e