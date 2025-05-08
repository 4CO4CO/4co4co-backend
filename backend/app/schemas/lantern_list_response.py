from pydantic import BaseModel


class LanternListResponseModel(BaseModel):
    id: int
    owner_name: str
    emotion: str
    is_current_user: bool
