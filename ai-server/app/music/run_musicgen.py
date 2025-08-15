import os
import tempfile
import torch
import torchaudio

from app.core.exceptions import GenerationError
from app.core.s3 import upload_file_to_s3
from app.music.model import model, model_lock, SAMPLE_RATE

def _build_prompt_from_emotion(emotion: str) -> str:
    base = (emotion or "").strip().lower()
    templates = {
        "happiness":      "a joyful, bright pop track with uplifting mood",
        "confidence":     "a confident, steady groove with clear motifs",
        "surprise":       "a playful track with unexpected turns and light textures",
        "pain":           "a melancholic, slow piece with sparse instrumentation",
        "disquietment":   "a tense, uneasy ambient underscore with evolving drones",
        "fear":           "a suspenseful cinematic cue with pulses and risers",
        "yearning":       "an emotional, longing ballad with gentle progression",
        "excitement":     "an energetic, upbeat track with driving rhythm",
        "embarrassment":  "a quirky, awkward-feel piece with light staccatos",
        "affection":      "a warm, intimate track with soft harmonies",
        "aversion":       "a dark, uneasy texture with dissonant layers",
        "engagement":     "a focused, steady groove with forward momentum",
        "anticipation":   "a subtle, building cue with gradual tension",
        "sensitivity":    "a delicate, tender ambient piece with soft pads",
        "annoyance":      "an edgy, restless motif with percussive accents",
        "sympathy":       "a gentle, compassionate track with mellow chords",
        "pleasure":       "a smooth, pleasant tune with relaxed rhythm",
    }
    return templates.get(base, f"a {base} ambient track" if base else "a soothing ambient track")

def generate_music(emotion: str, duration: int = 10) -> dict:
    """
    감정(emotion) 기반으로 MusicGen 생성 후 S3 업로드.
    반환: {"s3_key": "..."}
    """
    prompt = _build_prompt_from_emotion(emotion)

    try:
        with model_lock, torch.inference_mode():
            model.set_generation_params(duration=duration)
            out = model.generate([prompt], progress=False)  # out: list[tensor] 또는 tensor
    except Exception as e:
        raise GenerationError(f"Music generation failed: {e}") from e

    # --- 출력 정규화: list/tuple/tensor 모두 대응 ---
    tensor = None
    if isinstance(out, (list, tuple)):
        if len(out) == 0:
            raise GenerationError("Music generation returned empty list")
        first = out[0]
        if not torch.is_tensor(first) or first.numel() == 0:
            raise GenerationError("Music generation returned invalid tensor in list")
        tensor = first.detach().cpu()
    elif torch.is_tensor(out):
        if out.numel() == 0:
            raise GenerationError("Music generation returned empty tensor")
        t = out.detach().cpu()
        # 예상 가능한 형태:
        # (B, T) or (B, C, T) or (C, T) or (T,)
        if t.ndim == 3:         # (B, C, T)
            tensor = t[0]       # (C, T)
        elif t.ndim == 2:
            if t.shape[0] > 1:  # (B, T)
                tensor = t[0].unsqueeze(0)  # (1, T) -> (1, T), 아래에서 채널 정규화
            else:
                tensor = t      # (C, T) 또는 (1, T)
        elif t.ndim == 1:       # (T,)
            tensor = t.unsqueeze(0)  # (1, T)
        else:
            raise GenerationError(f"Unexpected tensor shape from generator: {tuple(t.shape)}")
    else:
        raise GenerationError(f"Unsupported output type from generator: {type(out)}")

    # --- (channels, frames) 형태로 정규화 ---
    if tensor.ndim == 1:
        tensor = tensor.unsqueeze(0)           # (T,) -> (1, T)
    elif tensor.ndim == 2:
        pass                                   # (C, T) or (1, T)
    else:
        # 혹시 남은 케이스 안전장치
        if tensor.ndim == 3 and tensor.shape[0] == 1:
            tensor = tensor.squeeze(0)         # (1, C, T) -> (C, T)
        else:
            raise GenerationError(f"Unexpected waveform shape after normalization: {tuple(tensor.shape)}")

    # dtype/연속성 보장
    if tensor.dtype != torch.float32:
        tensor = tensor.to(torch.float32)
    tensor = tensor.contiguous()


    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        torchaudio.save(
            tmp_path,
            tensor,
            sample_rate=SAMPLE_RATE,
            format="wav",
        )

        result = upload_file_to_s3(tmp_path)
        if not isinstance(result, dict) or not result.get("s3_key"):
            raise GenerationError("S3 upload returned no s3_key")

        return result

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
