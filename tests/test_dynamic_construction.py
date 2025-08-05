import json
import logging
import pathlib

import pytest

from dirconf import make_directory_config, register_handler

logging.getLogger().setLevel(logging.INFO)


class HandlerTest:
    def read(self, path):
        pass

    def write(self, path, data, overwrite_ok):
        pass


register_handler("test_handler", HandlerTest)


@pytest.fixture
def path_config() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "directory_config.json"


@pytest.fixture
def path_config_as_str(path_config) -> str:
    return str(path_config)


@pytest.fixture
def str_config(path_config) -> str:
    with path_config.open("r") as file:
        config_str = file.read()
    return config_str


@pytest.fixture
def dict_config(path_config) -> dict:
    with path_config.open("r") as file:
        config_dict = json.load(file)
    return config_dict


def test_dict_config(dict_config):
    _ = make_directory_config("TestConfig", dict_config)


def test_str_config(str_config):
    _ = make_directory_config("TestConfig", str_config)


def test_path_config(path_config):
    _ = make_directory_config("TestConfig", path_config)


def test_path_config_as_str(path_config_as_str):
    _ = make_directory_config("TestConfig", path_config_as_str)


def test_instantiation(dict_config):
    class_ = make_directory_config("TestConfig", dict_config)
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
