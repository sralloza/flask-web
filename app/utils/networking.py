"""Custom downloader with retries control."""
import logging

import requests

from .exceptions import DownloaderError
from . import MetaSingleton
logger = logging.getLogger(__name__)


class Downloader(requests.Session, metaclass=MetaSingleton):
    """Downloader with retries control."""

    def __init__(self, silenced=False, retries=5):
        self.logger = logging.getLogger(__name__)
        self.retries = retries

        if silenced is True:
            self.logger.setLevel(logging.CRITICAL)

        super().__init__()
        self.headers.update(
            {
                "User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
            }
        )

    def request(self, method, url, **kwargs):
        self.logger.debug("%s %r", method, url)
        retries = self.retries

        while retries > 0:
            try:
                return super().request(method, url, **kwargs)
            except requests.exceptions.ConnectionError:
                retries -= 1
                self.logger.warning(
                    "Connection error in %s, retries=%s", method, retries
                )
            except requests.exceptions.ReadTimeout:
                retries -= 1
                self.logger.warning("Timeout error in %s, retries=%s", method, retries)

        self.logger.critical("Download error in %s %r", method, url)
        raise DownloaderError("max retries failed.")


downloader = Downloader()
