---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.2
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Usage

<!-- begin basic -->

## Basic Usage

There are two essential steps for adapting `metaconf` to a specific use-case.

1. **Define handlers** satisfying the [`Handler`][metaconf.handler.Handler] protocol for each of the files present in your configuration.
2. **Define the structure of a valid configuration** in terms of its paths and their respective handlers, by subclassing the [`MetaConfig`][metaconf.config.MetaConfig] class. This is most easily done using the [`make_metaconfig`][metaconf.config.make_metaconfig] function.

The custom `MetaConfig` subclass can then be used to read and write configurations.

These steps are most easily understood through demonstration. See 

### Construct handlers for the files in the configuration

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

### Define a subclass of `MetaConfig`

```python
from metaconf import make_metaconfig

ConfigHandler = make_metaconfig(
    cls_name="ConfigHandler",
    config={"..."},
)
```

### Read and write configurations

```python
handler = ConfigHandler()
config = handler.read(path)

# ... modify the config, do whatever

handler.write(new_path, modified_config)
```

<!-- end basic -->
<!-- begin advanced -->

## Advanced Usage


### Nesting configurations within other configurations

### Handling missing files

```python
from metaconf.filter import filter, filter_missing

@filter(write=lambda path: not path.is_absolute())
@filter_missing(warn=True)
class YamlFileHandler:
    ...
```

### Absolute paths

### Validation

<!-- end advanced -->
