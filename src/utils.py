import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging(
    logging_folder: str = "logs", log_name: str = "app", logging_level=logging.INFO
):
    os.makedirs(logging_folder, exist_ok=True)
    handlers = [
        RotatingFileHandler(
            os.path.join(logging_folder, f"{log_name}.log"),
            encoding="utf8",
            maxBytes=1024 * 10240,
            backupCount=20,
        ),
        logging.StreamHandler(),
    ]

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s | %(name)s | [%(levelname)s] | %(message)s",
        handlers=handlers,
    )