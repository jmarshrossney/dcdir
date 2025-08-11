# Home

This is a simple tool for the meta-configuration of collections of configuration files, using Python [dataclasses](https://docs.python.org/3/library/dataclasses.html).

I wrote this because I sometimes work with quite old scientific models which tend to require various configuration files of different formats to be present in various places.

`metaconf` is a tool that

1. Allows the user to describe the structure of a directory representing a valid configuration, and validate real directories against this description.

2. Facilitate the generation of new configurations programmatically, in Python, as opposed to copying and editing files by hand or writing shell scripts.


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


## Usage

There are two essential steps for adapting `metaconf` to a specific use-case.

1. **Define handlers** satisfying the [`Handler`][metaconf.handler.Handler] protocol for each of the paths (files and directories) present in your configuration.
2. **Define the structure of a valid configuration** in terms of its paths and their respective handlers, by subclassing the [`MetaConfig`][metaconf.config.MetaConfig] class. This is most easily done using the [`make_metaconfig`][metaconf.config.make_metaconfig] function.

The custom `MetaConfig` subclass can then be used to

1. **Read** a configuration from the filesystem into a Python `dict` ([`MetaConfig.read`][metaconf.config.MetaConfig.read]). 
2. **Write** a configuration `dict` to the filesystem ([`MetaConfig.write`][metaconf.config.MetaConfig.write])

These steps are most easily understood through examples. See 


## Philosophy

I created this because

I wanted this tool to work alongside these other tools, without ever getting in the way or creating conflicts.


`metaconf` does not

- Come with any pre-built handlers or meta-configurations
- Provide any 

This is intentional.
It has no dependencies other than the Standard Library.

In particular, it is not in the scope of `metaconf` to perform validation of the actual configuration (this functionality is well-served by other tools).


