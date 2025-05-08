from datetime import datetime

import httpx

from app.core.exceptions.types import NotFoundError, AIResponseProcessingError
from app.repositories.lantern_repository import LanternRepository
from app.repositories.music_repository import MusicRepository
from app.schemas.db.music import MusicDBModel


class MusicService:
    def __init__(self, db):
        self.db = db
        self.user_repo = LanternRepository(db)
        self.music_repo = MusicRepository(db)

    async def generate_music(self, prompt: str, lantern_id: str):
        user = await self.user_repo.find_by_lantern_id(lantern_id)
        if not user:
            raise NotFoundError(f"Lantern ID {lantern_id} not found.")

        result = await self.mock_ai_client(prompt)
        file_path = result['data'].get('file_path')
        if not file_path:
            raise AIResponseProcessingError("No file path returned from AI")

        music_model = MusicDBModel(
            lantern_id=lantern_id,
            prompt=prompt,
            s3_path=file_path,
            created_at=datetime.utcnow()
        )

        await self.music_repo.save_music(music_model.model_dump(exclude={"id"}))
        return result

    @staticmethod
    async def call_ai_server(prompt: str):
        ai_server_url = "http://localhost:8001/api/v1/generate-music"
        try:
            async with httpx.AsyncClient(timeout=1000.0) as client:
                response = await client.post(ai_server_url, json={"prompt": prompt})
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            raise AIResponseProcessingError(f"Failed to fetch AI response: {str(e)}")

        if result['status'] != 'success':
            raise AIResponseProcessingError(f"AI returned error: {result['message']}")

        return result

    # ⚠️ [발표용 / 로컬 테스트용 MOCK]
    # 현재 로컬 환경에서는 GPU가 없어서 AI 서버 호출을 돌리기 어렵기 때문에
    # 아래 mock_ai_client 메서드를 준비함.
    # 이 메서드는 실제 서비스 배포 시 삭제 예정이며,
    # 배포 환경에서는 진짜 AI 서버 (call_ai_server)와 연결되어야 함.
    @staticmethod
    async def mock_ai_client(prompt: str):
        return {
            "status": "success",
            "message": "Mocked AI response",
            "data": {
                "file_path": f"s3://mock-bucket/{prompt.replace(' ', '_')}.mp3"
            }
        }
