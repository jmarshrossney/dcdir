import json
import logging
import pathlib

import pytest

from metaconf import make_metaconfig, register_handler

logging.getLogger().setLevel(logging.INFO)


class HandlerTest:
    def read(self, path):
        pass

    def write(self, path, data, overwrite_ok):
        pass


register_handler("test_handler", HandlerTest)


@pytest.fixture
def path_spec() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "spec.json"


@pytest.fixture
def path_spec_as_str(path_spec) -> str:
    return str(path_spec)


@pytest.fixture
def str_spec(path_spec) -> str:
    with path_spec.open("r") as file:
        spec_str = file.read()
    return spec_str


@pytest.fixture
def dict_spec(path_spec) -> dict:
    with path_spec.open("r") as file:
        spec_dict = json.load(file)
    return spec_dict


def test_dict_spec(dict_spec):
    _ = make_metaconfig("TestConfig", dict_spec)


def test_str_spec(str_spec):
    _ = make_metaconfig("TestConfig", str_spec)


def test_path_spec(path_spec):
    _ = make_metaconfig("TestConfig", path_spec)


def test_path_spec_as_str(path_spec_as_str):
    _ = make_metaconfig("TestConfig", path_spec_as_str)


def test_instantiation(dict_spec):
    class_ = make_metaconfig("TestConfig", dict_spec)
    # Test bfile given as path
    _ = class_(
            afile={"path": "afile.txt", "handler": "test_handler"},
            bfile="bfile.txt",
    )
    # Test bfile given as single-element dict
    _ = class_(
            afile={"path": "afile.txt", "handler": "test_handler"},
            bfile={"path": "bfile.txt"},
    )
