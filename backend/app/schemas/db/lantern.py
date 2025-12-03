from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class MusicStatusInfo(BaseModel):
    """
    Represents the processing status of music generation for a given image.
    Used for tracking Celery task progress.
    """
    image_s3: str
    task_id: str
    status: str  # 'pending', 'success', 'failed'
    s3_key: Optional[str] = None

    error_msg: Optional[str] = None
    updated_at: Optional[datetime] = None


class ImageInfo(BaseModel):
    """Metadata about an uploaded image."""
    s3_key: str
    original_filename: Optional[str] = None
    file_extension: Optional[str] = None
    file_size: Optional[int] = None


class MusicInfo(BaseModel):
    """Metadata about a generated music file."""
    s3_path: str
    created_at: datetime


class LanternDBModel(BaseModel):
    """
    Pydantic model representing a lantern document stored in MongoDB.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

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
        return str(id_value) if id_value else None