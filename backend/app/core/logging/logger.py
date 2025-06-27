import logging
import os


def get_logger(name: str):
    logger = logging.getLogger(name)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

        # 콘솔 로그 핸들러
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # 파일 로그 핸들러
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger
