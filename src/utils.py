import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(
    logging_folder: str = "logs", log_name: str = "app", logging_level: int = logging.INFO
) -> None:
    os.makedirs(logging_folder, exist_ok=True)

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s | %(name)s | [%(levelname)s] | %(message)s",
        handlers=[
            RotatingFileHandler(
                os.path.join(logging_folder, f"{log_name}.log"),
                encoding="utf8",
                maxBytes=1024 * 10240,
                backupCount=20,
            ),
            logging.StreamHandler()
        ]
    )