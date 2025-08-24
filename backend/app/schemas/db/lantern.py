from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class MusicStatusInfo(BaseModel):
    """
    Represents the processing status of music generation for a given image.
    """
    image_s3: str
    task_id: str
    status: str
    s3_key: Optional[str] = None


class ImageInfo(BaseModel):
    """
    Metadata about an uploaded image.
    """
    s3_path: str
    original_filename: Optional[str]
    file_extension: Optional[str]
    file_size: Optional[int]


class MusicInfo(BaseModel):
    """
    Metadata about a generated music file.
    """
    s3_path: str
    created_at: datetime


class LanternDBModel(BaseModel):
    """
    Pydantic model representing a lantern document stored in MongoDB.
    Includes metadata about images, music, and task statuses.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    lantern_id: str
    user_name: str
    images: List[ImageInfo] = []
    musics: List[MusicInfo] = []
    music_tasks: List[str] = []
    music_statuses: List[MusicStatusInfo] = []
    is_public: bool
    created_at: datetime

    @field_serializer('id')
    def serialize_objectid(self, id_value, _info):
        """
        Serialize MongoDB ObjectId to string when returning the model.
        Prevents issues with JSON encoding of ObjectId.
        """
        return str(id_value)
