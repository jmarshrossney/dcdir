import logging
import os
import pathlib

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
