from dirconf import Handler, DirectoryConfig


def test_dir_is_handler():
    assert isinstance(DirectoryConfig(), Handler)


def test_tree():
    d = DirectoryConfig()
    d.tree()
