from dcdir import Handler, FileConfig, DataclassDirectory

def test_dcdir_is_handler():
    assert isinstance(DataclassDirectory(), Handler)

def test_tree():
    d = DataclassDirectory()
    d.tree()
