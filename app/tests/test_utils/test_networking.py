import pytest

from app.utils import MetaSingleton
from app.utils.networking import Downloader


def test_use_singleton():
    assert type(Downloader) == MetaSingleton

    a = Downloader()
    b = Downloader()
    c = Downloader()

    assert a is b
    assert b is c
    assert c is a


@pytest.mark.xfail
class TestDownloader:
    def test_something(self):
        assert 0, "Not implemented"
