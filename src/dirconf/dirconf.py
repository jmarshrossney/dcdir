from collections.abc import Mapping
import dataclasses
import json
import functools
import logging
from os import PathLike
from pathlib import Path
from typing import Any, Callable

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

        print("Handler is: ", self.handler)

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


@dataclasses.dataclass
class DirectoryConfig:
    """Base dataclass to represent a directory."""

    def __post_init__(self) -> None:
        for f in dataclasses.fields(self):
            attr = getattr(self, f.name)

            if isinstance(attr, Node):
                continue

            elif isinstance(attr, (str, PathLike)):
                # Only path provided
                extension = Path(attr).suffix
                handlers = {
                    key: val["handler"]
                    for key, val in handler_registry.items()
                    if extension in val["extensions"]
                }
                if not handlers:
                    raise Exception(
                        f"No handler found for extension '{extension}' in the handler registry."
                    )
                if len(handlers) > 1:
                    logger.warning(
                        f"More than one handler found for extension '{extension}': {handlers}."
                    )
                handler = list(handlers.values())[0]
                logger.info("Using handler '{handler}' for field {f.name}")
                setattr(self, f.name, Node(path=attr, handler=handler))

            elif isinstance(attr, Mapping):
                # Mapping provided, attempt to create Node with it
                try:
                    config = Node(**attr)
                except TypeError as exc:
                    raise TypeError(
                        f"Field {f.name} must be an instance of Node"
                    ) from exc
                else:
                    setattr(self, f.name, config)

            else:
                raise TypeError(f"Field {f.name} must be an instance of Node")

    def read(self, path: str | PathLike) -> dict[str, Any]:
        path = Path(path).resolve()
        data = {}

        for f in dataclasses.fields(self):
            config = getattr(self, f.name)
            full_path = path / config.path
            handler = config.handler()

            data[f.name] = handler.read(full_path)

        return data

    def write(
        self, path: str | PathLike, data: dict[str, Any], *, overwrite_ok: bool = False
    ) -> None:
        path = Path(path).resolve()

        for f in dataclasses.fields(self):
            config = getattr(self, f.name)
            full_path = path / config.path
            handler = config.handler()

            this_data = data[f.name]

            handler.write(full_path, this_data, overwrite_ok=overwrite_ok)

    def tree(self, level: int = 1, print_: bool = True) -> list[str]:
        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "
        lines = []
        fields = dataclasses.fields(self)
        for i, f in enumerate(fields):
            config = getattr(self, f.name)
            handler = config.handler()

            lines += [level * pipe + (elbow if i == len(fields) else tee) + config.path]

            if isinstance(handler, DirectoryConfig):
                lines += handler.tree(level=level + 1, print_=False)

        if print_:
            print("\n".join(lines))

        return lines


@functools.singledispatch
def _make_directory_config(config, cls_name: str, **kwargs) -> type[DirectoryConfig]:
    raise NotImplementedError(f"Unsupported type: {type(config)}")


@_make_directory_config.register
def _(config: dict, cls_name: str, **kwargs) -> type[DirectoryConfig]:
    fields = []
    for name, spec in config.items():
        path = spec.get("path", False)
        handler = spec.get("handler", False)

        if not path and not handler:
            field = (name, Node)

        elif path and handler:
            field = (
                name,
                Node,
                dataclasses.field(
                    init=False,
                    default_factory=lambda: Node(
                        path=path, handler=handler_registry[handler]["handler"]
                    ),
                ),
            )

        elif "path" in spec and "handler" not in spec:
            raise NotImplementedError

        elif "path" not in spec and "handler" in spec:
            raise NotImplementedError

        else:
            raise Exception("Misconfigured...")

        fields.append(field)

    return dataclasses.make_dataclass(
        cls_name=cls_name,
        fields=fields,
        bases=(DirectoryConfig,),
        **kwargs,
    )


@_make_directory_config.register
def _(config: PathLike, cls_name: str, **kwargs) -> type[DirectoryConfig]:
    return _make_directory_config(json.load(config), cls_name, **kwargs)


@_make_directory_config.register
def _(config: str, cls_name: str, **kwargs) -> type[DirectoryConfig]:
    try:
        return _make_directory_config(Path(config), cls_name, **kwargs)
    except TypeError:
        return _make_directory_config(json.loads(config), cls_name, **kwargs)


def make_directory_config(
    cls_name: str, config: dict | str | PathLike, **kwargs
) -> type[DirectoryConfig]:
    return _make_directory_config(config, cls_name, **kwargs)
