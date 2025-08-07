from metaconf import Handler, MetaConfig


def test_metaconfig_is_handler():
    assert isinstance(MetaConfig(), Handler)


def test_tree():
    d = MetaConfig()
    d.tree()
