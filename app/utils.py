"""
Miscelaneous utilities.
"""

import inspect
import time
from functools import wraps
from typing import Callable

from src.logger import logger


def timed(func) -> Callable:
    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def timed_func(*args, **kwargs):
            init = time.perf_counter()
            out = await func(*args, **kwargs)
            end = time.perf_counter() - init
            logger.debug("%s finished in %.2f ms", func.__name__, 1000 * end)
            return out

    else:

        def timed_func(*args, **kwargs):
            init = time.perf_counter()
            out = func(*args, **kwargs)
            end = time.perf_counter() - init
            logger.debug("%s finished in %.2f ms", func.__name__, 1000 * end)
            return out

    return timed_func
