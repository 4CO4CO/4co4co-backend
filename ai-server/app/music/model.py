import torch
from threading import Lock
from contextlib import contextmanager
from typing import List
from audiocraft.models import MusicGen

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_lock = Lock()
model = MusicGen.get_pretrained("facebook/musicgen-small", device=device)
SAMPLE_RATE = getattr(model, "sample_rate", 32000)


@contextmanager
def model_session():
    """
    Context manager to safely use the MusicGen model.

    Ensures that:
    - Model parameter updates (set_generation_params)
    - Music generation calls (generate)

    are always executed within the same critical section,
    protected by model_lock.
    """
    with model_lock:
        yield model


def generate_locked(prompts: List[str], **gen_params):
    """
    Helper function to generate music with thread safety.

    Workflow:
    1. Acquire model lock via model_session
    2. Optionally update generation parameters
    3. Run model.generate() safely

    Example:
        generate_locked(["happy piano melody"], duration=10)

    Args:
        prompts (List[str]): List of text prompts for music generation
        **gen_params: Optional generation parameters (duration, etc.)

    Returns:
        Generated audio waveform (torch.Tensor or numpy array depending on model)
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
