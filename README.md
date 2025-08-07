# Metaconf

> [!IMPORTANT]
> This package is only a few days old. It is sparsely tested and entirely undocumented. Use at your own risk!

This is a simple tool for the meta-configuration of collections of configuration files, using Python dataclasses.

I wrote this because I sometimes work with quite old scientific models which tend to require various configuration files of different formats to be present in various places.

I wanted to have a tool that could:

1. Allow me to describe the structure of a directory representing a valid configuration, and validate real directories against this description.

2. Facilitate the generation of new configurations programmatically, in Python, as opposed to copying and editing files by hand or throwing together shell scripts.

That is pretty much it! I intend to keep this package extremely minimal.

In particular, it is not in the scope of `metaconf` to perform validation of the actual configuration (this functionality is well-served by other tools).

**More documentation to come.**
