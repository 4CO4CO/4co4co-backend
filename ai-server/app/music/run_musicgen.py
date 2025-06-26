import os
import re
import tempfile

import torchaudio

from app.core.exceptions import GenerationError
from app.core.s3 import upload_file_to_s3  # ✅ 여기서 import
from audiocraft.models import MusicGen

# 모델 로딩
model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(duration=10)


def sanitize_filename(prompt: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", prompt)[:30]


def generate_music(prompt: str, duration: int = 10) -> dict:
    model.set_generation_params(duration=duration)

    try:
        wav = model.generate([prompt], progress=False)
    except Exception as e:
        raise GenerationError(f"Music generation failed: {str(e)}") from e

    tensor = wav[0].cpu()

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            torchaudio.save(tmp.name, tensor, sample_rate=model.sample_rate, format="wav")
            tmp_path = tmp.name

        return upload_file_to_s3(tmp_path)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)