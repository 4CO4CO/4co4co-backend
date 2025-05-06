from datetime import datetime
import httpx

from app.core.exceptions import NotFoundError, AIResponseProcessingError
from app.repositories.music_repository import MusicRepository
from app.repositories.user_repository import UserRepository


class MusicService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)
        self.music_repo = MusicRepository(db)

    async def generate_music(self, prompt: str, user_key: str):
        # 사용자 존재 여부 확인
        user = await self.user_repo.find_user_by_key(user_key)
        if not user:
            raise NotFoundError(f"User with key {user_key} not found.")

        # AI 서버 호출
        result = await self.call_ai_server(prompt)
        file_path = result['data'].get('file_path')
        if not file_path:
            raise AIResponseProcessingError("No file path returned from AI")

        # DB에 음악 기록 저장
        await self.music_repo.save_user_music(
            user_key=user_key,
            prompt=prompt,
            s3_path=file_path,
            created_at=datetime.utcnow()
        )
        return result

    async def call_ai_server(self, prompt: str):
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
