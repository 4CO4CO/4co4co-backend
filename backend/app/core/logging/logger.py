import logging
import os
import requests
from app.core.config.settings import settings


class DiscordHandler(logging.Handler):

    def __init__(self, webhook_url: str, level=logging.ERROR):
        super().__init__(level)
        self.webhook_url = webhook_url

    def emit(self, record):

        try:
            summary = f"[{record.levelname}] {record.name} - {record.getMessage()}"

            if len(summary) > 1900:
                summary = summary[:1900] + "... (truncated)"

            payload = {"content": f":rotating_light: {summary}"}
            resp = requests.post(self.webhook_url, json=payload, timeout=5)

            if resp.status_code != 204:
                print(f"[DiscordHandler] Webhook failed: {resp.status_code} {resp.text}", flush=True)

        except Exception as e:
            print(f"[DiscordHandler] Failed to send log: {e}", flush=True)


def get_logger(name: str):

    logger = logging.getLogger(name)
    log_level = settings.LOG_LEVEL or "INFO"
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    if not logger.handlers:
        # console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # file handler
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # add discord handler
    if settings.DISCORD_WEBHOOK_URL and not any(isinstance(h, DiscordHandler) for h in logger.handlers):
        discord_handler = DiscordHandler(settings.DISCORD_WEBHOOK_URL, level=logging.ERROR)
        discord_handler.setFormatter(formatter)
        logger.addHandler(discord_handler)

        uvicorn_logger = logging.getLogger("uvicorn.error")
        if not any(isinstance(h, DiscordHandler) for h in uvicorn_logger.handlers):
            uvicorn_logger.addHandler(discord_handler)

    logger.propagate = False
    return logger
