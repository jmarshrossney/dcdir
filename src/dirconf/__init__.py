from typing import Annotated

from .handler import Handler as Handler, register_handler as register_handler
from .dirconf import (
    DirectoryConfig as DirectoryConfig,
    make_directory_config as make_directory_config,
)

class MISSING:
    """A sentinal value that may be used in place of missing data."""
