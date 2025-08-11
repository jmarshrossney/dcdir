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

<!-- begin usage -->
<!-- begin basic -->

## Basic Usage

#### A simple configuration

We will demonstrate basic usage of `metaconf` using a simple configuration containing a [YAML](https://en.wikipedia.org/wiki/YAML) file called `config.yml` and a [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file called `data.csv`.

A concrete instance of this configuration already exists in the `./basic` directory.

```python
from metaconf.utils import tree

print(tree("./basic"))
```

### Defining handlers

We first need to define two handlers that implement `read` and `write` for the two files that make up a configuration.


#### YAML handler

```python
from os import PathLike

import yaml

class YamlFileHandler:
    def read(self, path: str | PathLike) -> dict:
        with open(path, "r") as file:
            contents = yaml.safe_load(file)
        return contents

    def write(self, path: str | PathLike, data: dict, *, overwrite_ok: bool = False) -> None:
        with open(path, mode="w" if overwrite_ok else "x") as file:
            yaml.safe_dump(data, file, sort_keys=False)
```

Let's quickly test that `read` works:

```python
YamlFileHandler().read("./basic/config.yml")
```

#### CSV handler

```python
import csv

class CsvFileHandler:
    def read(self, path: str | PathLike) -> list[list[float]]:
        data = []
        with open(path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        return data

    def write(self, path: str | PathLike, data: list[list[float]], *, overwrite_ok: bool = False) -> None:
        with open(path, mode="w" if overwrite_ok else "x") as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow(row)

```

```python
CsvFileHandler().read("./basic/data.csv")
```

### Subclassing `MetaConfig`

The next step is to specify a valid configuration in terms of its files and handlers.

To do this we will use the [`make_metaconfig`][metaconf.config.make_metaconfig] function, which produces a subclass of [`MetaConfig`][metaconf.config.MetaConfig] whose fields correspond to the two required files.

```python
from metaconf import make_metaconfig

ConfigHandler = make_metaconfig(
    cls_name="ConfigHandler",
    spec={
        "config": {"path": "config.yml", "handler": YamlFileHandler},
        "data": {"path": "data.csv", "handler": CsvFileHandler},
    },
)
```

### Working with instances of `MetaConfig`


#### String representation

Instances of `MetaConfig` have a convenient string representation derived from [`MetaConfig.tree`][metaconf.config.MetaConfig.tree].

```python
handler = ConfigHandler()
print(handler)
```

#### Reading configurations

Once a `MetaConfig` is instantiated, configurations are read into a `dict` by passing a path to a configuration directory into the [`read`][metaconf.config.MetaConfig.read] method.

```python
config_dict = handler.read("./basic")

config_dict
```

#### Writing configurations

In-memory configurations can be written to the filesystem using the [`write`][metaconf.config.MetaConfig.write] method.

For the purpose of illustration we will modify the configuration and then write it to a temporary directory.

```python
import tempfile

# Modify the 'a' parameter
config_dict["config"]["params"]["a"] = -1.

with tempfile.TemporaryDirectory() as temp_dir:
    handler.write(temp_dir, config_dict)

    print(tree(temp_dir))
```

#### Accessing the nodes

Keep in mind that classes derived from `MetaConfig` as essentially [dataclasses](https://docs.python.org/3/library/dataclasses.html) whose fields are instances of [`Node`][metaconf.node.Node] (itself a dataclass!).
As such, the usual way of accessing dataclass fields applies.

```python
import dataclasses

for field in dataclasses.fields(handler):
    node = getattr(handler, field.name)
    print(field.name, "\t", type(node), "\t", node.path, "\t", node.handler)
```

!!! tip
    In the vast majority of situations (that I an think of) directly manipulating the nodes, paths or handlers after instantiation would be unnecessary.


<!-- end basic -->
<!-- begin advanced -->

## Advanced Usage


### Nesting configurations within other configurations

```python
print(tree("./nested"))
```

```python
NestedHandler = make_metaconfig(
    cls_name="NestedHandler",
    spec={
        "metadata": {"path": "metadata.yml", "handler": YamlFileHandler},
        "inner_config": {"path": "basic", "handler": ConfigHandler},
    },
)
```

```python
handler = NestedHandler()

print(handler)
```

```python
config_dict = handler.read("./nested")

config_dict
```

### Variable paths

Often configurations are flexible regarding paths and file names.

Here we do not fix the file name for `data` - perhaps it differs between configurations (e.g. based on a path set in `config.yml`).

```python
UnspecifiedPathHandler = make_metaconfig(
    cls_name="UnspecifiedPathHandler",
    spec={
        "config": {"path": "config.yml", "handler": YamlFileHandler},
        "data": {"handler": CsvFileHandler},
    },
)
```

`UnspecifiedPathHandler` now requires the **relative** path corresponding to `data` to be provided upon instantiation.

!!! note
    Under the hood, the provided path is transformed into a `Node` in the `__post_init__` dataclass method.

```python
handler = UnspecifiedPathHandler(data="data.csv")

print(handler)

handler.read("./basic")
```

### Variable paths and handlers

If we can delay specifying a path until instantiation, we may also want to delay the specification of the handler.

Let's say that the `config` node can be either a YAML or JSON file.

We first define a JSON handler.

```python
import json

class JsonFileHandler:
    def read(self, path: str | PathLike) -> dict:
        with open(path, "r") as file:
            contents = json.load(file)
        return contents

    def write(self, path: str | PathLike, data: dict, *, overwrite_ok: bool = False) -> None:
        with open(path, mode="w" if overwrite_ok else "x") as file:
            json.dump(data, file)
```

Now we construct a `MetaConfig` subclass that leaves `config` entirely unspecified.

```python
VariableHandler = make_metaconfig(
    cls_name="VariableHandler",
    spec={
        "config": {},
        "data": {"path": "data.csv", "handler": CsvFileHandler},
    },
)
```

We can now instantiate the class by passing a dict containing both the path and the handler.

```python
handler = VariableHandler(config={"path": "config.json", "handler": JsonFileHandler})
```

#### Registering handlers

To save some typing, we can register handlers to a handler registry.

```python
from metaconf import register_handler

register_handler("yaml", YamlFileHandler, extensions=[".yml", ".yaml"])
register_handler("json", JsonFileHandler, extensions=[".json"])
```

Now we can refer to handlers by their key in the registry.

```python
print(VariableHandler(config={"path": "config.json", "Handler": "json"}))
```

#### Handler inference

More usefully, we leave the handler to be inferred by the file extension.

We first load the original 'basic' configuration.

```python
yaml_handler = VariableHandler(config="config.yml")
print(yaml_handler)
yaml_handler.read("./basic")
```

Now we load the same configuration with a `.json` config file.

```python
json_handler = VariableHandler(config="config.json")
print(json_handler)
json_handler.read("./basic_json")
```

### Handling missing files

Up to this point, attempting to call `read` on a missing file or directory will result in an error being thrown. 

In some situations we might want to handle missing data differently. Sometimes certain files are optional, and one is simply happy to skip over them if they do not exist.

Another use-case would be reading from a 'template' configuration that is incomplete, requiring additional data which we will merge into the Python `dict` before writing the complete configuration to a new location.

```python
from metaconf.filter import filter_missing

@filter_missing(warn=True)
class DummyHandler:
    def read(self, path: str | PathLike) -> None:
        print("`read` has been called.")

    def write(self, path: str | PathLike, data: None, *, overwrite_existing: bool = False) -> None:
        print("`write` has been called.")
```

```python
ConfigHandler = make_metaconfig(
    cls_name="ConfigHandler",
    spec={
        "config": {"path": "config.yml", "handler": YamlFileHandler},
        "data": {"path": "data.csv", "handler": CsvFileHandler},
        "optional": {"path": "optional.file", "handler": DummyHandler},
    },
)
```

Let's try to read the usual configuration

```python
handler = ConfigHandler()

config = handler.read("./basic")
```

We see that `DummyHandler.read` was never called, and instead we are shown a warning that `read('optional.file')` was filtered out by a test (which we are shown the code for). Note that this warning can be disabled by setting `warn=False` (the default) in `filter_missing`. 

The configuration `dict` contains an entry corresponding to the `optional` node, but it has a special _sentinal_ value, [metaconf.filter.MISSING][].

```python
config
```

Now let's see what happens when we try to write the incomplete configuration.

```python
with tempfile.TemporaryDirectory() as temp_dir:
    handler.write(temp_dir, config)

    print(tree(temp_dir))
```

Once again we are shown a warning, which explains both what was filtered out and why, and `DummyHandler.write` was never called.


### Filtering

The `filter_missing` decorator is a special case of a more general [`filter`][metaconf.filter.filter] class decorator, which allows the user to specify tests which trigger the 'missingness' behaviour if they fail.

We will now briefly run through some illustrative examples where filtering comes in useful.

#### Skipping large files

As an example, we will consider a situation where one of the files in a configuration is very large, and we want to avoid loading it into memory.

This is easy to achieve by combining the already-familiar `filter_missing` with a custom filter applied to the `read` method, using [`filter_read`][metaconf.filter.filter_read]. 

We will demonstrate this by creating a subclass of `CsvFileHandler` from earlier.

```python
from metaconf.filter import filter_read

@filter_missing()
class PotentiallyLargeFileHandler(CsvFileHandler):

    @filter_read(test=lambda path: str(path) not in ["big.csv", "huge.csv"], label="skip large files")
    def read(self, path: str | PathLike) -> None:
        return super().read(path)

    def write(self, path: str | PathLike, data: None, *, overwrite_existing: bool = False) -> None:
        return super().write(path, data, overwrite_existing=overwrite_existing)
```

It should not be difficult to see why this works, but the following demonstrates it explicitly.

```python
ConfigHandler = make_metaconfig(
    cls_name="ConfigHandler",
    spec={
        "a": {"handler": PotentiallyLargeFileHandler},
        "b": {"handler": PotentiallyLargeFileHandler},
        "c": {"handler": PotentiallyLargeFileHandler},
    },
)

print(tree("./sizes"))

handler = ConfigHandler(
    a="small.csv",
    b="big.csv",
    c="huge.csv",
)

config = handler.read("./sizes")

config
```


#### Skipping absolute paths

```python
from metaconf.filter import filter

@filter(
    read=lambda path: not path.is_absolute(),
    write=lambda path, data, **_: not path.is_absolute()
)
class SaferCsvFileHandler(CsvFileHandler):
    pass

ConfigHandler = make_metaconfig(
    cls_name="ConfigHandler",
    spec={
        "config": {"path": "config.yml", "handler": YamlFileHandler},
        "data": {"path": "data.csv", "handler": SaferCsvFileHandler},
        "big_data": {"path": "/path/to/shared/data.csv", "handler": SaferCsvFileHandler},
    }
)

handler = ConfigHandler()
print(handler)
```

```python
config = handler.read("./basic/")

config
```

```python
with tempfile.TemporaryDirectory() as temp_dir:
    handler.write(temp_dir, config)

    print(tree(temp_dir))
```


#### Generating metadata

In this example, we will read an incomplete configuration from `./basic`, and only upon `write` will we inject metadata into the configuration.

```python
from metaconf.filter import filter_missing

ConfigHandler = make_metaconfig(
    cls_name="ConfigHandler",
    spec={
        "config": {"path": "config.yml", "handler": YamlFileHandler},
        "data": {"path": "data.csv", "handler": CsvFileHandler},
        "metadata": {"path": "metadata.csv", "handler": filter_missing()(CsvFileHandler)},
    },
)

handler = ConfigHandler()

config = handler.read("./basic")

print(config["metadata"])
```

*Not yet finished.*


### Strategies for validation

*To do.*


<!-- end advanced -->
<!-- end usage -->
