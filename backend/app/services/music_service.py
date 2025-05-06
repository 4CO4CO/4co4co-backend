import requests
from app.core.exceptions import AIResponseProcessingError


def generate_music(prompt: str):
    ai_server_url = "http://localhost:8001/api/v1/generate-music"
    try:
        response = requests.post(ai_server_url, json={"prompt": prompt})
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        raise AIResponseProcessingError(message=f"Failed to fetch AI response: {str(e)}")

    # 응답 후 처리
    if result['status'] != 'success':
        raise AIResponseProcessingError(message=f"AI returned error: {result['message']}")

    # 파일 경로 확인
    file_path = result['data'].get('file_path')
    if not file_path:
        raise AIResponseProcessingError(message="No file path returned from AI")

    return result
