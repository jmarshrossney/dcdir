import functools
from os import PathLike
from pathlib import Path
from typing import Callable, Any
import warnings

from .handler import Handler


class MISSING:
    """A sentinal value that may be used in place of missing data."""


class MissingWarning(Warning):
    pass


def handle_missing(
    test_on_read: Callable[[Path], bool] = lambda path: Path(path).exists(),
    test_on_write: Callable[[Path, Any, ...], bool] = (
        lambda path, data, **_: data is not MISSING
    ),
):
    """A decorator for Handler classes."""

    def decorator(cls: Handler):
        original_read = cls.read
        original_write = cls.write

        @functools.wraps(original_read)
        def wrapped_read(self, path: str | PathLike) -> Any:
            if not test_on_read(Path(path)):
                warnings.warn(
                    f'read("{path}") failed missingness test; returning `MISSING`.',
                    MissingWarning,
                )
                return MISSING

            return original_read(self, path)

        @functools.wraps(original_write)
        def wrapped_write(self, path: str | PathLike, data: Any, **kwargs) -> None:
            if not test_on_write(Path(path), data, **kwargs):
                warnings.warn(
                    f'write("{path}") failed missingness test; Skipping...',
                    MissingWarning,
                )
                return

            return original_write(self, path, data, **kwargs)

        cls.read = wrapped_read
        cls.write = wrapped_write

        return cls

    return decorator
