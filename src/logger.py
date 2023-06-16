"""
Logger object
"""

import logging
from os import environ


def setup_logger(name="zeroshot_summarizer", log_level: int = logging.INFO):
    if log_level == logging.DEBUG:
        format_str = (
            "%(asctime)s | %(levelname)s | %(name)s - [%(module)s.%(funcName)s]: %(message)s"
        )
    else:
        format_str = "%(asctime)s | %(levelname)s | %(name)s: %(message)s"
    logging.basicConfig(format=format_str)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger


logger = setup_logger(log_level=logging.DEBUG if "DEBUG" in environ else logging.INFO)
