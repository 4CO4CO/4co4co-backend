import tempfile
from pathlib import Path

import torch

from audiocraft.data.audio import audio_write
from audiocraft.models import MusicGen

# 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# 모델 불러오기
model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(duration=10)

def generate_music(prompt: str, duration: int = 10) -> str:
    model.set_generation_params(duration=duration)
    wav = model.generate([prompt], progress=False)
    tensor = wav[0].cpu()

    # 임시 파일로 저장
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "sample.wav"
        audio_write(
            stem_name=str(tmp_path).replace(".wav", ""),
            wav=tensor,
            sample_rate=model.sample_rate,
            format="wav",
            strategy="loudness"
        )
        return "success"
