import logging
from abc import ABC, abstractmethod
from threading import Thread
from typing import List

S = List[str]
logger = logging.getLogger(__name__)


class BaseParser(ABC):
    def __init__(self, dmm):
        self.dmm = dmm

    @classmethod
    @abstractmethod
    def load(cls, dmm, urls: S = None):
        raise NotImplementedError

    @abstractmethod
    def process_url(self, url: str, retries=5):
        raise NotImplementedError


class BaseWorker(ABC, Thread):
    def __init__(self, url: str, html_parser: BaseParser, retries: int = 5):
        super().__init__()
        self.url = url
        self.html_parser = html_parser
        self.retries = retries

    def run(self):
        """Runs the thread."""
        logger.debug('Starting %s with url %s', type(self).__name__, self.url)
        self.html_parser.process_url(self.url, self.retries)
