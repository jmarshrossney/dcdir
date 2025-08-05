from abc import abstractmethod
from collections import OrderedDict
import logging
from os import PathLike
from typing import Any, Callable, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class Handler(Protocol):
    @abstractmethod
    def read(self, path: str | PathLike) -> Any: ...

    @abstractmethod
    def write(self, path: str | PathLike, data: Any, *, overwrite_ok: bool) -> None: ...


handler_registry: OrderedDict = OrderedDict({})


def register_handler(
    name: str, handler: Callable[[], Handler], extensions: list[str] = []
) -> None:
    if name in handler_registry:
        logger.warning(
            f"'{name}' already exists in handler registry, and will be overwritten!"
        )

    assert isinstance(name, str)
    assert isinstance(handler(), Handler)

    assert all([isinstance(ext, str) for ext in extensions])
    assert all([ext.startswith(".") for ext in extensions])

    handler_registry[name] = {
        "handler": handler,
        "extensions": extensions,
    }
