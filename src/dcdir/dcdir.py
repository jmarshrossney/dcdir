from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, fields
import logging
from os import PathLike
from pathlib import Path
from typing import Any, ClassVar, Protocol, runtime_checkable, Self

logger = logging.getLogger(__name__)


@runtime_checkable
class Handler(Protocol):
    @abstractmethod
    def read(self, path: str | PathLike) -> Any: ...

    @abstractmethod
    def write(self, path: str | PathLike, data: Any, *, overwrite_ok: bool) -> None: ...


@dataclass
class FileConfig:
    path: Path
    handler: Handler

    def __post_init__(self) -> None:
        assert self.path is not None
        path = Path(self.path)

        # Do not allow absolute paths or paths include '..'
        if path.expanduser().is_absolute():
            raise Exception("`path` should be relative, not absolute")
        if not path.resolve().is_relative_to(Path.cwd()):
            raise Exception("`path` should not include '..'")

        self.path = path

        # TODO: check handler is a class adhering to Handler protocol


@dataclass
class DataclassDirectory:
    """Base dataclass to represent a directory."""

    def __post_init__(self) -> None:
        for f in fields(self):
            attr = getattr(self, f.name)

            if isinstance(attr, FileConfig):
                continue

            # NOTE: is it even worth supporting this?
            elif isinstance(attr, Handler):
                # Handler but no path provided. In this case the handler
                # may attempt to infer the correct path based on the field name
                logger.info(
                    f"A handler but no path was provided for field '{f.name}'. The handler may be able to infer the path."
                )
                setattr(self, f.name, FileConfig(f.name, handler))

            elif isinstance(attr, Mapping):
                # Mapping provided, attempt to create FileConfig with it
                try:
                    config = FileConfig(**attr)
                except TypeError as exc:
                    raise TypeError(f"Field {f.name} must be an instance of FileConfig")
                else:
                    setattr(self, f.name, config)

            else:
                raise TypeError(f"Field {f.name} must be an instance of FileConfig")

    def read(self, path: str | PathLike) -> dict[str, Any]:
        path = Path(path).resolve()
        data = {}

        for f in fields(self):
            config = getattr(self, f.name)
            full_path = path / config.path
            handler = config.handle

            data[f.name] = handler.read(full_path)

        return data

    def write(
        self, path: str | PathLike, data: dict[str, Any], *, overwrite_ok: bool = False
    ) -> None:
        path = Path(path).resolve()

        for f in fields(self):
            config = getattr(self, f.name)
            full_path = path / config.path
            handler = config.handler

            this_data = data[f.name]

            handler.write(full_path, this_data, overwrite_ok=overwrite_ok)


    def tree(self, level: int = 1, print_: bool = True) -> list[str]:
        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "
        lines = []
        fields_ = fields(self)
        for i, f in enumerate(fields_):
            config = getattr(self, f.name)

            lines += [level * pipe + (elbow if i == len(fields_) else tee) + config.path]

            if isinstance(config.handler, DataclassDirectory):
                lines += config.handler.tree(level=level + 1, print_=False)

        if print_:
            print("\n".join(lines))

        return lines
