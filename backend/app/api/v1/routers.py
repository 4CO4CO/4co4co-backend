from fastapi import APIRouter

from app.api.v1 import music_api, lantern_api, websocket

api_router = APIRouter()

api_router.include_router(music_api.router, tags=["music"])
api_router.include_router(lantern_api.router, tags=["lanterns"])
api_router.include_router(websocket.router, prefix="/ws")

