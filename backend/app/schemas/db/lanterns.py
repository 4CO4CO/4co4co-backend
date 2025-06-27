from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class LanternsDBModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    lantern_id: str
    user_name: str
    image_path: str
    original_filename: Optional[str] = None
    file_extension: Optional[str] = None
    file_size: Optional[int] = None
    is_public: bool
    created_at: datetime

    @field_serializer('id')
    def serialize_objectid(self, id_value, _info):
        return str(id_value)
