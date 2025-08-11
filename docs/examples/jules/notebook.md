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

# Configuration of the JULES land surface model


Some background about the JULES land surface model.

Documentation is available at [https://jules-lsm.github.io](https://jules-lsm.github.io).

```python
from os import PathLike
from pathlib import Path

import metaconf
```

## Namelists

<!-- #region -->
The JULES executable is run by passing the path to a directory containing these namelists as its sole positional argument,

```sh
jules.exe /path/to/namelists/
```

where `namelists/` must contain _all_ of the required namelists files,

```txt
namelists/
├── ancillaries.nml
├── crop_params.nml
├── drive.nml
├── fire.nml
├── imogen.nml
├── initial_conditions.nml
├── jules_deposition.nml
├── jules_hydrology.nml
├── jules_irrig.nml
├── jules_prnt_control.nml
├── jules_radiation.nml
├── jules_rivers.nml
├── jules_snow.nml
├── jules_soil_biogeochem.nml
├── jules_soil.nml
├── jules_surface.nml
├── jules_surface_types.nml
├── jules_vegetation.nml
├── jules_water_resources.nml
├── model_environment.nml
├── model_grid.nml
├── nveg_params.nml
├── output.nml
├── pft_params.nml
├── prescribed_data.nml
├── science_fixes.nml
├── timesteps.nml
├── triffid_params.nml
└── urban.nml
```

!!! note
    There is no freedom to use different file names for the namelist files; they must be present exactly as specified above.
<!-- #endregion -->

We will make use of the [`f90nml`](https://f90nml.readthedocs.io/en/latest/) Python package[^1] for reading and writing namelist files.

[^1]: Marshall Ward. (2019). marshallward/f90nml: Version 1.1.2 (v1.1.2). Zenodo. [https://doi.org/10.5281/zenodo.3245482](https://doi.org/10.5281/zenodo.3245482)

```python
import f90nml

class NamelistFileHandler:
    def read(self, path: str | PathLike) -> dict:
        """Read a Fortran namelist file and return a dict of its contents."""
        data = f90nml.read(path)
        return data.todict()

    def write(
        self, path: str | PathLike, data: dict, *, overwrite_ok: bool = False
    ) -> None:
        """Write a dict to a Fortran namelist file."""
        f90nml.write(data, path, force=overwrite_ok)

```

We now construct a `MetaConfig`-based Handler for a namelists directory, in which each `Node` corresponds to a single `.nml` file with a fixed path and handler.

```python
_jules_namelists = [
    "ancillaries",
    "crop_params",
    "drive",
    "fire",
    "imogen",
    "initial_conditions",
    "jules_deposition",
    "jules_hydrology",
    "jules_irrig",
    "jules_prnt_control",
    "jules_radiation",
    "jules_rivers",
    "jules_snow",
    "jules_soil_biogeochem",
    "jules_soil",
    "jules_surface",
    "jules_surface_types",
    "jules_vegetation",
    "jules_water_resources",
    "model_environment",
    "model_grid",
    "nveg_params",
    "output",
    "pft_params",
    "prescribed_data",
    "science_fixes",
    "timesteps",
    "triffid_params",
    "urban",
]

NamelistDirectoryHandler = metaconf.make_metaconfig(
    cls_name="NamelistDirectoryHandler",
    spec={
        name: {"path": f"{name}.nml", "handler": NamelistFileHandler}
        for name in _jules_namelists
    },
)
```

This produces a subclass of `MetaConfig` which is instantiated without any arguments.

```python
namelists_handler = NamelistDirectoryHandler()

print(namelists_handler)
```

We can now use this handler to read an entire namelists directory into a Python dict.

```python
namelists_dict = namelists_handler.read("config/namelists")

namelists_dict.keys()
```

```python
namelists_dict["drive"]
```

## Input data


### Ascii input data


JULES also requires 

We can use `numpy` to read and write floating point ascii data.

```python
from typing import TypedDict
import numpy

@metaconf.handle_missing(
    test_on_read=lambda path: path.exists(),
    test_on_write=lambda path, data, **_: not (
        data is metaconf.MISSING or path.is_absolute()
    ),
)
class AsciiFileHandler:
    class AsciiData(TypedDict):
        values: numpy.ndarray
        comment: str

    def read(self, path: str | PathLike) -> AsciiData:
        comment_lines = []
        num_lines = 0

        with open(path, "r") as file:
            for line in file:
                line = line.strip()

                if line.startswith(("#", "!")):  # comment line
                    comment_lines.append(line)
                    continue

                elif line:  # non-empty line
                    num_lines += 1

                    if num_lines > 1:  # we just need to know if it's >1
                        break

        comment = "\n".join(comment_lines)

        values = numpy.loadtxt(str(path), comments=("#", "!"))

        # NOTE: Unfortunately numpy.loadtxt/savetxt does not correctly round-trip
        # single-row data. We need to catch it here and add an extra dimension.
        if num_lines == 1:
            assert values.ndim == 1
            values = values.reshape(1, -1)

        return self.AsciiData(values=values, comment=comment)

    def write(
        self,
        path: str | PathLike,
        data: AsciiData,
        *,
        overwrite_ok: bool = False,
    ) -> None:
        numpy.savetxt(
            str(path),
            data["values"],
            fmt="%.5f",
            header=data["comment"],
            comments="#",
        )

```

### NetCDF input data


We will use `xarray` to read and write input data in the `netCDF` format.

```python
import xarray

@metaconf.handle_missing(
    test_on_read=lambda path: path.exists() and not path.is_absolute(),
    test_on_write=lambda path, data, **_: not (
        data is metaconf.MISSING or path.is_absolute()
    ),
)
class NetcdfFileHandler:
    def read(self, path: str | PathLike) -> xarray.Dataset:
        dataset = xarray.load_dataset(path)
        return dataset

    def write(
        self, path: str | PathLike, data: xarray.Dataset, *, overwrite_ok: bool = False
    ) -> None:
        if not overwrite_ok and Path(path).is_file():
            raise FileExistsError(f"There is already a file at '{path}'")
        data.to_netcdf(path)


```

## Putting it together

```python
metaconf.register_handler("ascii", AsciiFileHandler, [".txt", ".dat", ".asc"])
metaconf.register_handler("netcdf", NetcdfFileHandler, [".nc", ".cdf"])

```

```python
InputFilesConfig = metaconf.make_metaconfig(
    cls_name="InputFilesConfig",
    spec={
        "initial_conditions": {
            "handler": AsciiFileHandler,
        },
        "tile_fractions": {
            "handler": AsciiFileHandler,
        },
        "driving_data": {},
    },
)

```

```python
JulesConfigHandler = metaconf.make_metaconfig(
    cls_name="JulesConfigHandler",
    spec={
        "inputs": {},  # we will fix this upon instantiation
        "namelists": {"handler": NamelistDirectoryHandler},  # fully fixed

    },
)

```

## Reading an existing configuration

```python
from metaconf.utils import tree
    
print(tree("./config"))
```

```python
handler = JulesConfigHandler(
    namelists="namelists",
    inputs={
        "path": "inputs",
        "handler": lambda: InputFilesConfig(
            initial_conditions="initial_conditions.dat",
            tile_fractions="tile_fractions.dat",
            driving_data="Loobos_1997.dat",
        )
    }
)

print(handler)
```

```python
config = handler.read("./config")

config.keys()
```

## Reading with netcdf


```python
handler = JulesConfigHandler(
    namelists="namelists",
    inputs={
        "path": "inputs",
        "handler": lambda: InputFilesConfig(
            initial_conditions="initial_conditions.dat",
            tile_fractions="tile_fractions.dat",
            driving_data="Loobos_1997.nc",
        )
    }
)

print(handler)
```

```python
config = handler.read("./config")

config.keys()
```

```python
config["inputs"]["driving_data"]
```


## Writing a new configuration


We will now demonstrate how to generate a new JULES configuration based on a modification of the existing one.

Here we will use `tempfile` to write to a temporary directory that is automatically deleted upon exit from the context handler. In practice one would create a persistent directory.

```python
import tempfile

config = handler.read("./config")

print("current output period: ", config["namelists"]["output"]["jules_output_profile"]["output_period"])

config["namelists"]["output"]["jules_output_profile"]["output_period"] = 3600

with tempfile.TemporaryDirectory() as temp_dir:

    handler.write(temp_dir, config)

    print(tree(temp_dir))
```

