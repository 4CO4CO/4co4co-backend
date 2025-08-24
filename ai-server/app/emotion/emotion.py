import random


_FAKE_EMOTIONS = ["happy", "sad", "calm", "angry", "excited"]


def extract_emotion(image_path: str) -> str:
    """
    Dummy function for emotion extraction.
    Currently returns a random emotion from a fixed list.
    TODO: Replace with actual emotion extraction pipeline.

    Args:
        image_path (str): Path or key of the input image

    Returns:
        str: Detected emotion label
    """
    # Pick a random emotion for now
    return random.choice(_FAKE_EMOTIONS)
