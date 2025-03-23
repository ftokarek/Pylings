# pylings/logger.py
import logging
from pathlib import Path

def setup_logging(log_file: Path = None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove old handlers
    for h in logger.handlers:
        logger.removeHandler(h)

    formatter = logging.Formatter("%(asctime)s - %(name)s: %(message)s")

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        # Default to console if no file provided
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
