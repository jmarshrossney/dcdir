from abc import abstractmethod
from collections import OrderedDict
import importlib
import logging
from os import PathLike
import pathlib
from typing import Any, Callable, Protocol, runtime_checkable, TypeAlias

logger = logging.getLogger(__name__)


@runtime_checkable
class Handler(Protocol):
    """A Protocol for all valid handlers."""

    @abstractmethod
    def read(self, path: str | PathLike) -> Any: ...

    @abstractmethod
    def write(self, path: str | PathLike, data: Any, *, overwrite_ok: bool) -> None: ...


HandlerFactory: TypeAlias = Callable[[], Handler]

handler_registry: OrderedDict = OrderedDict({})


def register_handler(
    name: str, handler: HandlerFactory, extensions: list[str] = []
) -> None:
    """Add a handler factory to the registry."""
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


def parse_handler(input: str | HandlerFactory) -> HandlerFactory:
    """Returns a `HandlerFactory given any valid input."""
    if input in handler_registry:
        handler = handler_registry[input]["handler"]
    elif isinstance(input, str):
        module_name, class_name = input.rsplit(".", 1)
        module = importlib.import_module(module_name)
        handler = getattr(module, class_name)
    elif callable(input) and isinstance(input(), Handler):
        handler = input
    else:
        raise TypeError(f"Invalid handler: '{input}'")

    return handler


def infer_handler_from_path(path: str | PathLike) -> HandlerFactory:
    """Infers the desired HandlerFactory based on the file extension."""
    extension = pathlib.Path(path).suffix
    compatible_handlers = {
        key: val["handler"]
        for key, val in handler_registry.items()
        if extension in val["extensions"]
    }
    if not compatible_handlers:
        raise Exception(
            f"No handler found for extension '{extension}' in the handler registry."
        )
    if len(compatible_handlers) > 1:
        logger.warning(
            f"Multiple compatible handlers found for extension '{extension}'."
        )
    return list(compatible_handlers.values())[-1]
