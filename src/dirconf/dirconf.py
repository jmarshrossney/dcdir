from abc import abstractmethod
from collections.abc import Mapping
import dataclasses
import logging
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class Handler(Protocol):
    @abstractmethod
    def read(self, path: str | PathLike) -> Any: ...

    @abstractmethod
    def write(self, path: str | PathLike, data: Any, *, overwrite_ok: bool) -> None: ...


_handler_registry: dict[str, Callable[[], Handler]] = {}


def register_handler(extension: str, handler: Callable[[], Handler]) -> None:
    assert isinstance(handler(), Handler)

    assert isinstance(extension, str)
    assert extension.startswith(".")

    if extension in _handler_registry:
        logger.warning(
            f"Extension '{extension}' already exists in handler registry and will be overwritten!"
        )

    _handler_registry[extension] = handler


@dataclasses.dataclass
class FileConfig:
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

        self.path = path

        assert isinstance(self.handler(), Handler)


@dataclasses.dataclass
class DataclassDirectory:
    """Base dataclass to represent a directory."""

    def __post_init__(self) -> None:
        for f in dataclasses.fields(self):
            attr = getattr(self, f.name)

            if isinstance(attr, FileConfig):
                continue

            elif isinstance(attr, (str, PathLike)):
                # Only path provided
                extension = Path(attr).suffix
                try:
                    handler = _handler_registry[extension]
                except KeyError as exc:
                    raise Exception(
                        f"No handler found for extension '{extension}' in the handler registry."
                    ) from exc
                else:
                    setattr(self, f.name, FileConfig(path=attr, handler=handler))

            elif isinstance(attr, Mapping):
                # Mapping provided, attempt to create FileConfig with it
                try:
                    config = FileConfig(**attr)
                except TypeError as exc:
                    raise TypeError(
                        f"Field {f.name} must be an instance of FileConfig"
                    ) from exc
                else:
                    setattr(self, f.name, config)

            else:
                raise TypeError(f"Field {f.name} must be an instance of FileConfig")

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

            if isinstance(handler, DataclassDirectory):
                lines += handler.tree(level=level + 1, print_=False)

        if print_:
            print("\n".join(lines))

        return lines


# TODO: make more flexible, e.g. fixed paths
def make_dataclass_directory(
    cls_name: str,
    field_names: list[str],
) -> DataclassDirectory:
    return dataclasses.make_dataclass(
        cls_name=cls_name,
        fields=[(name, FileConfig) for name in field_names],
        bases=(DataclassDirectory,),
    )
