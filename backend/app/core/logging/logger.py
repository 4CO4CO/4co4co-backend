import logging
import os
import requests
from app.core.config.settings import settings


class DiscordHandler(logging.Handler):
    """
    Custom logging handler that sends log messages to a Discord channel via webhook.
    - Posts error-level (or above) messages to the given webhook URL
    - Truncates messages if they exceed Discord's 2000-character limit
    """

    def __init__(self, webhook_url: str, level=logging.ERROR):
        super().__init__(level)
        self.webhook_url = webhook_url

    def emit(self, record):
        """
        Format and send a log record to Discord.
        """
        try:
            # Compose a summary with only level, logger name, and message
            summary = f"[{record.levelname}] {record.name} - {record.getMessage()}"

            # Truncate if Discord message length exceeds ~2000 characters
            if len(summary) > 1900:
                summary = summary[:1900] + "... (truncated)"

            payload = {"content": f":rotating_light: {summary}"}
            # requests is synchronous, acceptable for error logging
            resp = requests.post(self.webhook_url, json=payload, timeout=5)

            # Discord webhook returns 204 No Content on success
            if resp.status_code != 204:
                print(f"[DiscordHandler] Webhook failed: {resp.status_code} {resp.text}", flush=True)

        except Exception as e:
            print(f"[DiscordHandler] Failed to send log: {e}", flush=True)


def get_logger(name: str):
    """
    Get or create a logger
    """
    logger = logging.getLogger(name)

    # Set log level from settings or default to INFO
    log_level = getattr(settings, "LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    # Avoid adding duplicate console/file handlers
    if not logger.handlers:
        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # File handler
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Add Discord handler only once
        if settings.DISCORD_WEBHOOK_URL:
            if not any(isinstance(h, DiscordHandler) for h in logger.handlers):
                discord_handler = DiscordHandler(settings.DISCORD_WEBHOOK_URL, level=logging.ERROR)
                discord_handler.setFormatter(formatter)
                logger.addHandler(discord_handler)

            # Also attach the same Discord handler to uvicorn.error logger
            uvicorn_logger = logging.getLogger("uvicorn.error")
            if not any(isinstance(h, DiscordHandler) for h in uvicorn_logger.handlers):
                discord_handler = DiscordHandler(settings.DISCORD_WEBHOOK_URL, level=logging.ERROR)
                discord_handler.setFormatter(formatter)
                uvicorn_logger.addHandler(discord_handler)

    # Prevent log messages from propagating to parent loggers
    logger.propagate = False
    return logger
