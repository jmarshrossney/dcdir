# Metaconf

> [!IMPORTANT]
> This package is only a few days old. It is sparsely tested. Use at your own risk!


`metaconf` is a simple tool for the meta-configuration of collections of configuration files, leaning heavily on Python [dataclasses](https://docs.python.org/3/library/dataclasses.html).

I wrote this because I sometimes work with quite old scientific models requiring various configuration files and data inputs in various formats to be present in various locations. I was (and remain) concerned about how easy it can be to misconfigure certain models without realising, and how common workflows compromise reproducibility.

`metaconf` helps by

1. Allowing the user to describe the structure of a directory representing a valid configuration, and validate real directories against this description.

2. Facilitating the generation of new configurations and metadata programmatically, in Python, as opposed to copying and editing files by hand or writing shell scripts.

3. Providing a consistent mechanism through which complex, distributed configurations in legacy formats can be validated using excellent tools such as [JSON Schema](https://json-schema.org/) and [Pydantic](https://docs.pydantic.dev/).

For user documentation and examples please visit [https://jmarshrossney.github.io/metaconf/](https://jmarshrossney.github.io/metaconf/).


## Getting started

This project uses [`uv`](https://docs.astral.sh/uv/), although you are free to substitute this with other tools for working on Python projects.

Install the project and development dependencies by running

```sh
uv sync
```

You can now run the tests in the repository root with

```sh
uv run pytest
```

Before contributing, consider installing [`pre-commit`](https://pre-commit.com/) so that the pre-commit hooks run before each commit.

```sh
uv tool install pre-commit
```

## Building the example notebooks

The following command will convert all markdown `.md` notebooks to Jupyter `.ipynb` notebooks, and execute them.

```sh
uv run --group examples jupytext --set-formats ipynb,md --execute docs/examples/*/*.md
```

## Building the documentation

After building the notebooks, simply run

```sh
uv run mkdocs serve
```

to build the documentation and display it in your browser.


## Contributing

Contributions are welcome! Please open a Pull Request against the `develop` branch.

However, please keep in mind that the overarching goal of this project is to be as simple as possible (while still being useful).

