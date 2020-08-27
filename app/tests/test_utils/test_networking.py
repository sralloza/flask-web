from collections import Counter
from unittest import mock

import pytest
from requests import exceptions as req_exc

from app.utils import MetaSingleton
from app.utils.exceptions import DownloaderError
from app.utils.networking import USER_AGENT, Downloader

REQUESTS_EXCEPTIONS = (
    req_exc.URLRequired,
    req_exc.TooManyRedirects,
    req_exc.HTTPError,
    req_exc.ConnectionError,
    req_exc.ConnectTimeout,
    req_exc.ReadTimeout,
)


def test_use_singleton():
    assert type(Downloader) == MetaSingleton

    a = Downloader()
    b = Downloader()
    c = Downloader()

    assert a is b
    assert b is c
    assert c is a


@mock.patch("requests.Session.request")
class TestDownloader:
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        Downloader._instance = None

    def test_init_declaration(self, *args):
        downloader = Downloader()
        assert hasattr(downloader, "logger")
        assert hasattr(downloader, "retries")

        assert downloader.headers["User-Agent"] == USER_AGENT

    def test_get(self, request_mock, caplog):
        caplog.set_level(10)
        downloader = Downloader()
        downloader.get("some-url")
        request_mock.assert_called_with("GET", "some-url", allow_redirects=True)
        assert "GET 'some-url'" in caplog.text

    def test_post(self, request_mock, caplog):
        caplog.set_level(10)
        downloader = Downloader()
        downloader.post("some-url", data="data", json="json")
        request_mock.assert_called_with("POST", "some-url", data="data", json="json")
        assert "POST 'some-url'" in caplog.text

    def test_delete(self, request_mock, caplog):
        caplog.set_level(10)
        downloader = Downloader()
        downloader.delete("some-url")
        request_mock.assert_called_with("DELETE", "some-url")
        assert "DELETE 'some-url'" in caplog.text

    def test_put(self, request_mock, caplog):
        caplog.set_level(10)
        downloader = Downloader()
        downloader.put("some-url", data="data")
        request_mock.assert_called_with("PUT", "some-url", data="data")
        assert "PUT 'some-url'" in caplog.text

    def test_head(self, request_mock, caplog):
        caplog.set_level(10)
        downloader = Downloader()
        downloader.head("some-url")
        # Default allow_redirects for HEAD is false
        request_mock.assert_called_with("HEAD", "some-url", allow_redirects=False)
        assert "HEAD 'some-url'" in caplog.text

    @pytest.mark.parametrize("error_class", REQUESTS_EXCEPTIONS)
    @pytest.mark.parametrize("retries", range(1, 5))
    @pytest.mark.parametrize("nerrors", range(5))
    def test_retry_control(self, request_mock, caplog, nerrors, retries, error_class):
        request_mock.side_effect = [error_class] * nerrors + ["response"]
        caplog.set_level(10)

        downloader = Downloader(retries=retries)

        if nerrors > downloader.retries:
            with pytest.raises(DownloaderError):
                downloader.post("some-url", "data", "json")
        else:
            downloader.post("some-url", "data", "json")

        request_mock.assert_called()
        logger_method_count = Counter([x.levelname for x in caplog.records])

        if nerrors:
            assert "%s in POST" % error_class.__name__ in caplog.text

        if nerrors > downloader.retries:
            assert request_mock.call_count == downloader.retries + 1
            assert logger_method_count["DEBUG"] == 1
            assert logger_method_count["INFO"] == 0
            assert logger_method_count["WARNING"] == downloader.retries + 1
            assert logger_method_count["CRITICAL"] == 1
        else:
            assert request_mock.call_count == nerrors + 1
            assert logger_method_count["DEBUG"] == 1
            assert logger_method_count["INFO"] == 0
            assert logger_method_count["WARNING"] == nerrors
            assert logger_method_count["CRITICAL"] == 0
