from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime


class MusicDBModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_key: str
    prompt: str
    s3_path: str
    created_at: datetime

    @field_serializer('id')
    def serialize_objectid(self, id_value, _info):
        return str(id_value)
