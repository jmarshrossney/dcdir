import functools
from os import PathLike
from pathlib import Path
from typing import Callable, Any

from .handler import Handler


class MISSING:
    """A sentinal value that may be used in place of missing data."""


# TODO: consider adding logging


def handle_missing_in_read(
    test: Callable[[Path], bool] = lambda path: path.exists(),
):
    def decorator(reader):
        @functools.wraps(reader)
        def wrapper(self, path: str | PathLike):
            return reader(self, path) if test(Path(path)) else MISSING

        return wrapper

    return decorator


def handle_missing_in_write(
    test: Callable[[Path, Any, ...], bool] = (
        lambda path, data, **_: data is not MISSING
    ),
):
    def decorator(writer):
        @functools.wraps(writer)
        def wrapper(self, path: str | PathLike, data: Any, **kwargs):
            test(Path(path), data, **kwargs) and writer(self, path, data, **kwargs)

        return wrapper

    return decorator


def handle_missing(
    test_on_read: Callable[[Path], bool] = lambda path: Path(path).exists(),
    test_on_write: Callable[[Path, Any, ...], bool] = (
        lambda path, data, **_: data is not MISSING
    ),
):
    def decorator(cls: Handler):
        original_read = cls.read
        original_write = cls.write

        @functools.wraps(original_read)
        def wrapped_read(self, path: str | PathLike) -> Any:
            return original_read(self, path) if test_on_read(Path(path)) else MISSING

        @functools.wraps(original_write)
        def wrapped_write(self, path: str | PathLike, data: Any, **kwargs) -> None:
            test_on_write(Path(path), data, **kwargs) and original_write(
                self, path, data, **kwargs
            )

        cls.read = wrapped_read
        cls.write = wrapped_write

        return cls

    return decorator
