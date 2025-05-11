import json
import asyncio
import redis.asyncio as aioredis
from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from app.core.config.settings import settings

router = APIRouter()

# Redis 클라이언트 (async)
redis_subscriber = aioredis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)

# 연결된 WebSocket 클라이언트 저장용 (lantern_id별 관리)
active_connections: dict[str, list[WebSocket]] = {}


@router.websocket("/lanterns/{lantern_id}")
async def websocket_endpoint(websocket: WebSocket, lantern_id: str):
    await websocket.accept()
    print(f"[WebSocket] Connected: {lantern_id}")

    # 연결 리스트에 저장
    if lantern_id not in active_connections:
        active_connections[lantern_id] = []
    active_connections[lantern_id].append(websocket)

    try:
        pubsub = redis_subscriber.pubsub()
        await pubsub.subscribe("lantern_updates")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                if data.get("lantern_id") == lantern_id:
                    print(f"[WebSocket] Sending to {lantern_id}: {data}")
                    await websocket.send_json(data)

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print(f"[WebSocket] Disconnected: {lantern_id}")
        active_connections[lantern_id].remove(websocket)
        if not active_connections[lantern_id]:
            del active_connections[lantern_id]
    finally:
        await pubsub.unsubscribe("lantern_updates")
        await pubsub.close()
