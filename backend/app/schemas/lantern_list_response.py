from pydantic import BaseModel


class LanternListResponseModel(BaseModel):
    id: int
    title: str
    owner_name: str
    emotion: str
    is_current_user: bool
