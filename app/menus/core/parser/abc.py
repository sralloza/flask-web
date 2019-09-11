import logging
from abc import ABC, abstractmethod
from typing import List

S = List[str]
logger = logging.getLogger(__name__)


class BaseParser(ABC):
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("Parsers can't be instanciated")

    @staticmethod
    @abstractmethod
    def process_url(dmm, text: str, retries=5):
        raise NotImplementedError
