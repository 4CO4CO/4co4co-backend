from pydantic import BaseModel


class LanternListResponseModel(BaseModel):
    lantern_id: str
    owner_name: str
    emotion: str
    is_current_lantern: bool
