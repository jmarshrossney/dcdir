import dataclasses
import logging
from os import PathLike
from pathlib import Path
from typing import Callable

from .handler import Handler, infer_handler_from_path, parse_handler

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Node:
    path: Path
    handler: Callable[[], Handler]

    def __post_init__(self) -> None:
        # Parsing + validation of path
        assert self.path is not None
        path = Path(self.path)
        # Do not allow absolute paths or paths include '..'
        if path.expanduser().is_absolute():
            raise ValueError("`path` should be relative, not absolute")
        if not path.resolve().is_relative_to(Path.cwd()):
            raise ValueError("`path` should not include '..'")

        # Parsing + validation of handler
        handler = parse_handler(self.handler)
        assert callable(handler)
        try:
            handler_inst = handler()
        except TypeError as exc:
            raise TypeError("`handler` must be a zero-argument callable!") from exc
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

        return Node(path=path, handler=handler or infer_handler_from_path(path))

    return transform


def to_node(input: Node | dict | str | PathLike) -> Node:
    if isinstance(input, Node):
        return input
    if isinstance(input, dict) and "handler" in input:
        return dict_to_node(input)
    if isinstance(input, (str, PathLike)) or (
        isinstance(input, dict) and "handler" not in input
    ):
        return path_to_node()(input)

    raise TypeError(f"Unable to create Node object from input of type {type(input)}")
