import dataclasses
import json
import logging
from os import PathLike
from pathlib import Path
from typing import Any, Self

from .node import Node, path_to_node, to_node

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MetaConfig:
    """A base dataclass representing a collection of configuration files."""

    def __post_init__(self) -> None:
        for field in dataclasses.fields(self):
            if (transform := field.metadata.get("transform")) is not None:
                # Apply transform if specified
                setattr(self, field.name, transform(getattr(self, field.name)))

            if not isinstance(getattr(self, field.name), Node):
                # try to coerce to a Node
                setattr(self, field.name, to_node(getattr(self, field.name)))

    def __call__(self) -> Self:
        # TODO: figure out if this is sufficient for nested MetaConfig objects
        return type(self)(**dataclasses.asdict(self))

    def read(self, path: str | PathLike) -> dict[str, Any]:
        path = Path(path)
        data = {}

        for field in dataclasses.fields(self):
            config = getattr(self, field.name)
            full_path = path / config.path
            handler = config.handler()

            data[field.name] = handler.read(full_path)

        return data

    def write(
        self, path: str | PathLike, data: dict[str, Any], *, overwrite_ok: bool = False
    ) -> None:
        path = Path(path)

        if not path.is_dir():
            logger.info(f"Creating new directory at '{path.resolve()}'")
            path.mkdir(parents=True)

        for field in dataclasses.fields(self):
            config = getattr(self, field.name)
            full_path = path / config.path
            handler = config.handler()

            this_data = data[field.name]

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

            if isinstance(handler, MetaConfig):
                lines += handler.tree(level=level + 1, print_=False)

        if print_:
            print("\n".join(lines))

        return lines


def _make_metaconfig(cls_name: str, config: dict, **kwargs) -> type[MetaConfig]:
    fields = []
    for name, spec in config.items():
        path = spec.get("path", False)
        handler = spec.get("handler", False)

        # Both path and handler specified in config
        if path and handler:
            field = (
                name,
                Node,
                dataclasses.field(
                    init=False, default_factory=lambda p=path, h=handler: Node(p, h)
                ),
            )
            # Note that the *current* values of path, handler are bound to the lambda
            # function through the explicit arguments. That is, `lambda: Node(path, handler)`
            # is wrong since the path, handler will be the values from the final iteration!

        # Only handler specified
        elif handler and not path:
            field = (
                name,
                Node,
                dataclasses.field(metadata={"transform": path_to_node(handler)}),
            )

        # Only path specified
        elif path and not handler:
            raise NotImplementedError(
                f"A handler should be specified for the path '{path}'."
            )

        # Neither path nor handler specified
        else:
            field = (name, Node, dataclasses.field(metadata={"transform": to_node}))

        fields.append(field)

    return dataclasses.make_dataclass(
        cls_name=cls_name,
        fields=fields,
        bases=(MetaConfig,),
        **kwargs,
    )


def _str_is_json(s: str) -> bool:
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


def _str_is_path(s: str) -> bool:
    try:
        path = Path(s)
        return path.exists() or path.is_absolute() or path.is_relative_to(Path.cwd())
    except (OSError, ValueError):
        return False


def make_metaconfig(
    cls_name: str, config: dict | str | PathLike, **kwargs
) -> type[MetaConfig]:
    if isinstance(config, dict):
        return _make_metaconfig(cls_name, config, **kwargs)

    if isinstance(config, str) and _str_is_json(config):
        return _make_metaconfig(cls_name, json.loads(config), **kwargs)

    if isinstance(config, PathLike) or (
        isinstance(config, str) and _str_is_path(config)
    ):
        with open(config, "r") as file:
            loaded_config = json.load(file)
        return _make_metaconfig(cls_name, loaded_config, **kwargs)

    raise TypeError(f"Unsupported type: {type(config)}")
