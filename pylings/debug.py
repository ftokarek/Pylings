import logging
from pylings.constants import DEBUG_PATH

def setup_logging(debug: bool):
    """Configure application-wide logging based on debug flag.

    If debug mode is enabled, logs are written to a file defined by `DEBUG_PATH`.
    The log format includes timestamps, log level, module, and message.

    Args:
        debug (bool): Whether to enable detailed logging to file.
    """
    handlers = []

    if debug:
        handlers.append(logging.FileHandler(DEBUG_PATH, mode="w"))

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            handlers=handlers
        )