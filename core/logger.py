import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import BASE_DIR


def get_logger():
    logger = logging.getLogger("banking_sim")
    if logger.handlers:
        return logger

    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    handler = RotatingFileHandler(log_dir / "banking_sim.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = get_logger()
