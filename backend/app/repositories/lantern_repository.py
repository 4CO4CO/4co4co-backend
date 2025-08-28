from typing import Optional

from app.core.exceptions.types import DatabaseError


class LanternRepository:
    """
    Repository class for interacting with the 'lantern' collection in MongoDB.
    Provides CRUD-like methods with error handling using custom DatabaseError.
    """

    def __init__(self, db):
        # Reference to the 'lantern' collection
        self.collection = db.lantern

    async def insert_lantern(self, user_doc):
        """
        Insert a new lantern document into the collection.
        Args:
            user_doc (dict): Document to insert
        Returns:
            InsertOneResult object
        Raises:
            DatabaseError: if insertion fails
        """
        try:
            result = await self.collection.insert_one(user_doc)
            return result
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_by_lantern_id(self, lantern_id):
        """
        Find a lantern document by its lantern_id.
        Args:
            lantern_id (str): The lantern identifier
        Returns:
            dict or None: The found document or None if not found
        Raises:
            DatabaseError: if query fails
        """
        try:
            return await self.collection.find_one({"lantern_id": lantern_id})
        except Exception as e:
            raise DatabaseError(f"find_by_lantern_id failed for {lantern_id}: {e}") from e

    async def count_documents(self, filter_dict):
        """
        Count documents in the collection matching the given filter.
        Args:
            filter_dict (dict): MongoDB query filter
        Returns:
            int: number of matching documents
        Raises:
            DatabaseError: if query fails
        """
        try:
            return await self.collection.count_documents(filter_dict)
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def exists_by_lantern_id(self, lantern_id: str) -> bool:
        """
        Check if a lantern with the given lantern_id exists.
        Args:
            lantern_id (str): The lantern identifier
        Returns:
            bool: True if exists, False otherwise
        Raises:
            DatabaseError: if query fails
        """
        try:
            document = await self.collection.find_one({"lantern_id": lantern_id}, {"_id": 1})
            return document is not None
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_random_lanterns(self, limit: int = 20, exclude_lantern_id: Optional[str] = None):
        """
        Retrieve random lantern documents that are public.
        Args:
            limit (int): Number of documents to sample (default 20)
            exclude_lantern_id (str, optional): Lantern ID to exclude from results
        Returns:
            list: A list of randomly sampled documents
        Raises:
            DatabaseError: if query fails
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
        Args:
            lantern_id (str): Lantern identifier
            image_key (str): Image S3 key to match inside music_statuses
            task_id (str): Celery task ID to set
        Returns:
            bool: True if a document was modified, False otherwise
        Raises:
            DatabaseError: if query fails
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

