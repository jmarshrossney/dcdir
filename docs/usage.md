# Usage

The main task when using `metaconf` is to subclass the `MetaConfig` dataclass to your specific configuration.

## Construct handlers for the files in the configuration

Say we have a `.yaml` file...

```python
from os import PathLike

import yaml

class YamlFileHandler:
    def read(self, path: str | PathLike) -> dict:
        with open(path, "r") as file:
            contents = yaml.safe_load(file)
        return contents

    def write(self, path: str | PathLike, data: dict, *, overwrite_ok: bool = False) -> None:
        with open(path, "w") as file:
            yaml.safe_dump(file)
```

### Optional: add handler filters

```python
from metaconf.filter import filter, filter_missing

@filter(write=lambda path: not path.is_absolute())
@filter_missing(warn=True)
class YamlFileHandler:
    ...
```

### Optional: gather files into subdirectories

To do

## Define a subclass of `MetaConfig`

```python
from metaconf import make_metaconfig

ConfigHandler = make_metaconfig(
    cls_name="ConfigHandler",
    config={"..."},
)
```

## Read and write configurations

```python
handler = ConfigHandler()
config = handler.read(path)

# ... modify the config, do whatever

handler.write(new_path, modified_config)
```

## Next steps...

- Validation of configurations

Take a look at the examples.
