import logging
import os
import pathlib
from typing import Iterator

logger = logging.getLogger(__name__)


class switch_dir:
    """Context manager for changing to *existing* directory."""

    def __init__(self, path: str | os.PathLike) -> None:
        self.new = pathlib.Path(path)

        if not self.new.is_dir():
            raise (
                NotADirectoryError(f"{self.new} is not a directory")
                if self.new.exists()
                else FileNotFoundError(f"{self.new} does not exist")
            )

    def __enter__(self):
        logger.debug("Switching directory to %s" % self.new)
        self.old = pathlib.Path.cwd()
        os.chdir(self.new)

    def __exit__(self, etype, value, traceback):
        logger.debug("Switching directory back to %s" % self.old)
        os.chdir(self.old)


def _tree(path: pathlib.Path, prefix: str) -> Iterator[str]:
    blank = "   "
    pipe = "│  "
    tee = "├──"
    elbow = "└──"

    contents = sorted(path.iterdir())
    pointers = [tee] * (len(contents) - 1) + [elbow]

    for pointer, path_ in zip(pointers, contents):
        yield prefix + pointer + path_.name

        if path_.is_dir():
            extension = pipe if pointer == tee else blank
            yield from _tree(path_, prefix=prefix + extension)


def tree(path: str | os.PathLike) -> str:
    """
    Construct a tree-like representation of a directory.

    Note:
      This is inspired by [GNU `tree`](https://linux.die.net/man/1/tree) and
      is an adaptation of [this stackoverflow answer](https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python) by Aaron Hall.
    """
    return path + "\n" + "\n".join(list(_tree(pathlib.Path(path), prefix="")))
