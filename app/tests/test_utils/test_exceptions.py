import pytest

from app.utils.exceptions import AppError, DownloaderError


class TestAppError:
    def test_inheritance(self):
        exc = AppError()
        assert isinstance(exc, AppError)
        assert isinstance(exc, Exception)

    def test_raise(self):
        with pytest.raises(AppError):
            raise AppError


class TestDownloaderError:
    def test_inheritance(self):
        exc = DownloaderError()
        assert isinstance(exc, DownloaderError)
        assert isinstance(exc, AppError)

    def test_raise(self):
        with pytest.raises(DownloaderError):
            raise DownloaderError
