# Home

`metaconf` is a simple tool for the meta-configuration of collections of configuration files, leaning heavily on Python [dataclasses](https://docs.python.org/3/library/dataclasses.html).

I wrote this because I sometimes work with quite old scientific models requiring various configuration files and data inputs in various formats to be present in various locations. I was (and remain) concerned about how easy it can be to misconfigure certain models without realising, and how common workflows compromise reproducibility.

`metaconf` helps by

1. Allowing the user to describe the structure of a directory representing a valid configuration, and validate real directories against this description.

2. Facilitating the generation of new configurations and metadata programmatically, in Python, as opposed to copying and editing files by hand or writing shell scripts.

3. Providing a consistent mechanism through which complex, distributed configurations in legacy formats can be validated using excellent tools such as [JSON Schema](https://json-schema.org/) and [Pydantic](https://docs.pydantic.dev/).


## Installation

`metaconf` is a Python package and thus can be installed using `pip`, or tools such as `uv` and `poetry` that wrap around `pip`.


=== "pip"

    ```sh
    pip install git+https://github.com/jmarshrossney/metaconf
    ```

=== "uv"

    ```sh
    uv add git+https://github.com/jmarshrossney/metaconf
    ```

!!! Note
    Currently `metaconf` is not in PyPI and must be installed directly from Github.

Currently Python versions equal to or above 3.11 are supported.
It has no dependencies other than the Standard Library.


## Overview of usage

There are two essential steps for adapting `metaconf` to a specific use-case.

1. **Define handlers** satisfying the [`Handler`][metaconf.handler.Handler] protocol for each of the paths (files and directories) present in your configuration.
2. **Define the structure of a valid configuration** in terms of its paths and their respective handlers, by subclassing the [`MetaConfig`][metaconf.config.MetaConfig] class. This is most easily done using the [`make_metaconfig`][metaconf.config.make_metaconfig] function.

The custom `MetaConfig` subclass can then be used to

1. **Read** a configuration from the filesystem into a Python `dict` ([`MetaConfig.read`][metaconf.config.MetaConfig.read]). 
2. **Write** a configuration `dict` to the filesystem ([`MetaConfig.write`][metaconf.config.MetaConfig.write])

These steps are most easily understood through examples. To start with, take a look at the [Usage](examples/101/notebook.ipynb) section. More realistic examples can be found in the right navigation bar.

All of the examples (include 'Usage') are based on Jupyter notebooks. Instructions for building the notebooks locally can be found in the `README.md` file in the [GitHub repository](https://github.com/jmarshrossney/metaconf).


## Philosophy

I have no intention of developing `metaconf` into a more sophisticated tool than it already is. The aim is that is works seamlessly alongside other tools and packages for parsing and validation, without ever getting in the way or creating conflicts.

With that out of the way, please feel free to raise an [issue](https://github.com/jmarshrossney/metaconf/issues) or make a [pull request](https://github.com/jmarshrossney/metaconf/pulls) to suggest a change or feature.
