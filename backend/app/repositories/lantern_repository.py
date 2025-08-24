from typing import Optional

from app.core.exceptions.types import DatabaseError


class LanternRepository:
    def __init__(self, db):
        self.collection = db.lantern

    async def insert_lantern(self, user_doc):
        try:
            result = await self.collection.insert_one(user_doc)
            return result
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_by_lantern_id(self, lantern_id):
        try:
            return await self.collection.find_one({"lantern_id": lantern_id})
        except Exception as e:
            raise DatabaseError(f"find_by_lantern_id failed for {lantern_id}: {e}") from e

    async def count_documents(self, filter_dict):
        try:
            return await self.collection.count_documents(filter_dict)
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def exists_by_lantern_id(self, lantern_id: str) -> bool:
        try:
            document = await self.collection.find_one({"lantern_id": lantern_id}, {"_id": 1})
            return document is not None
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_random_lanterns(self, limit: int = 20, exclude_lantern_id: Optional[str] = None):
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

