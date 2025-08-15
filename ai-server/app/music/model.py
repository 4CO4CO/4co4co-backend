import torch
from threading import Lock
from contextlib import contextmanager
from typing import List
from audiocraft.models import MusicGen

# 디바이스 결정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 모델 & 락
model_lock = Lock()
model = MusicGen.get_pretrained("facebook/musicgen-small", device=device)

# 샘플레이트
SAMPLE_RATE = getattr(model, "sample_rate", 32000)

@contextmanager
def model_session():
    """
    권장 사용법: 모델 상태 변경(set_generation_params)과 generate를
    항상 같은 크리티컬 섹션에서 수행하기 위한 컨텍스트 매니저.
    """
    with model_lock:
        yield model

def generate_locked(prompts: List[str], **gen_params):
    """
    권장 헬퍼: 파라미터 설정 + 생성까지 락으로 보호.
    예) generate_locked([prompt], duration=10)
    """
    with model_session() as m:
        if gen_params:
            m.set_generation_params(**gen_params)
        return m.generate(prompts, progress=False)

__all__ = [
    "model",
    "model_lock",
    "model_session",
    "generate_locked",
    "SAMPLE_RATE",
    "device",
]
