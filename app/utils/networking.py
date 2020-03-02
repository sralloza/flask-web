"""Custom downloader with retries control."""
import logging

import requests

from .exceptions import DownloaderError
from . import MetaSingleton

logger = logging.getLogger(__name__)

USER_AGENT = (
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
)


class Downloader(requests.Session, metaclass=MetaSingleton):
    """Downloader with retries control."""

    def __init__(self, retries=5):
        self.logger = logging.getLogger(__name__)
        self.retries = retries

        super().__init__()
        self.headers.update({"User-Agent": USER_AGENT})

    def request(self, method, url, **kwargs):
        self.logger.debug("%s %r", method, url)
        retries = self.retries

        while retries >= 0:
            try:
                return super().request(method, url, **kwargs)
            except requests.exceptions.RequestException as exc:
                retries -= 1
                self.logger.warning(
                    "%s in %s, retries=%s", type(exc).__name__, method, retries
                )

        self.logger.critical("Download error in %s %r", method, url)
        raise DownloaderError("max retries failed.")


downloader = Downloader()
