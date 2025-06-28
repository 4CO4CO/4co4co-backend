import os
import tempfile

import torchaudio

from app.core.exceptions import GenerationError
from app.core.s3 import upload_file_to_s3
from audiocraft.models import MusicGen

# 모델 로드 (한 번만)
model = MusicGen.get_pretrained("facebook/musicgen-small")


def generate_music(
    description: str,
    image: str,
    duration: int = 10,
) -> dict:
    """
    description: 텍스트 설명 (현재는 사용하지 않음)
    image: 단일 이미지 S3 경로
    duration: 생성할 음악 길이(초)
    """
    # 매 호출마다 duration 재설정
    model.set_generation_params(duration=duration)

    # TODO: 나중에 description/images 기반 프롬프트를 생성할 것
    hardcoded_prompt = "a soothing ambient track"

    try:
        wav = model.generate([hardcoded_prompt], progress=False)
    except Exception as e:
        raise GenerationError(f"Music generation failed: {e}") from e

    tensor = wav[0].cpu()
    tmp_path = None

    try:
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            torchaudio.save(
                tmp.name,
                tensor,
                sample_rate=model.sample_rate,
                format="wav"
            )
            tmp_path = tmp.name

        # S3에 업로드 후 결과 리턴
        return upload_file_to_s3(tmp_path)

    finally:
        # 임시 파일 정리
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)