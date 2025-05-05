from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class UserDBModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: ObjectId = Field(alias="_id")
    user_key: str
    name: str
    image_path: str

    @field_serializer('id')
    def serialize_objectid(self, id_value, _info):
        return str(id_value)
