import functools
from os import PathLike
from pathlib import Path
from typing import Callable, Any


class MISSING:
    """A sentinal value that may be used in place of missing data."""


def skip_read(
    test: Callable[[Path], bool] = lambda path: not path.exists(),
    sentinal: Any = MISSING,
):
    def decorator(reader):
        @functools.wraps(reader)
        def wrapper(self, path: str | PathLike):
            return sentinal if test(Path(path)) else reader(path)

        return wrapper

    return decorator


def skip_write(
    test: Callable[[Path, Any], bool] = lambda path, data: data is MISSING,
    sentinal: Any = MISSING,
):
    def decorator(writer):
        @functools.wraps(writer)
        def wrapper(self, path: str | PathLike, data: Any, **kwargs):
            return sentinal if test(Path(path), data) else writer(path)

        return wrapper

    return decorator
