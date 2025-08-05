import dataclasses
import logging
from os import PathLike
from pathlib import Path
from typing import Callable

from .handler import Handler, handler_registry

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Node:
    path: Path
    handler: Callable[[], Handler]

    def __post_init__(self) -> None:
        assert self.path is not None
        path = Path(self.path)

        # Do not allow absolute paths or paths include '..'
        if path.expanduser().is_absolute():
            raise Exception("`path` should be relative, not absolute")
        if not path.resolve().is_relative_to(Path.cwd()):
            raise Exception("`path` should not include '..'")

        handler = self.handler
        if isinstance(handler, str):
            try:
                handler = handler_registry[handler]["handler"]
            except KeyError:
                pass  # TODO: throw error here?

        assert callable(handler)
        try:
            handler_inst = handler()
        except TypeError as exc:
            raise Exception("`handler` must be a zero-argument callable!") from exc
        else:
            assert isinstance(handler_inst, Handler)

        self.path = path
        self.handler = handler


def dict_to_node(path_and_handler: dict) -> Node:
    return Node(**path_and_handler)


def path_to_node(
    handler: Callable[[], Handler] | None = None,
) -> Callable[str | PathLike, Node]:
    def transform(path: str | PathLike | dict[str, str | PathLike]) -> Node:
        # Might pass argument as single-element dict {"path": path}
        if isinstance(path, dict):
            path = path["path"]

        _handler = handler
        if _handler is None:
            extension = Path(path).suffix
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
            _handler = list(compatible_handlers.values())[0]

        return Node(path=path, handler=_handler)

    return transform


def to_node(input: Node | dict | str | PathLike) -> Node:
    if isinstance(input, Node):
        return input
    elif isinstance(input, dict):
        return dict_to_node(input)
    elif isinstance(input, (str, PathLike)):
        return path_to_node()(input)
    else:
        raise TypeError(
            f"Unable to create Node object from input of type {type(input)}"
        )


# TODO: a catch-all transform that's added to metadata by default, which works
# when the dataclass was instantiated with a Node instance (not a dict).
