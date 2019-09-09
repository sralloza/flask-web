import logging
from abc import ABC, abstractmethod
from threading import Thread
from typing import List

S = List[str]
logger = logging.getLogger(__name__)


class BaseParser(ABC):
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("Parsers can't be instanciated")

    @staticmethod
    @abstractmethod
    def process_url(dmm, url: str, retries=5):
        raise NotImplementedError


class BaseWorker(ABC, Thread):
    parser = BaseParser

    def __init__(self, dmm, url: str, retries: int = 5):
        super().__init__()
        self.dmm = dmm
        self.url = url
        self.retries = retries

    def run(self):
        """Runs the thread."""
        logger.debug('Starting %s with url %r', type(self).__name__, self.url)
        self.parser.process_url(self.dmm, self.url, retries=self.retries)
