import logging
import os
from logging.handlers import RotatingFileHandler

from config.config import BASE_DIR, DATA_DIR

LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "f1_press_bot.log"

def setup_logging():
    env = os.getenv("APP_ENV", "development").lower()
    log_level = os.getenv("LOG_LEVEL", "INFO" if env == "production" else "DEBUG").upper()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=3
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("TeleBot").setLevel(logging.CRITICAL)