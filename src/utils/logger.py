import logging
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    logs_path = Path("src/data/logs")
    logs_path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logs_path / "scraper.log", encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
