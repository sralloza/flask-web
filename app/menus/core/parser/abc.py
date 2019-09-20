import logging
from abc import ABC, abstractmethod
from typing import List

S = List[str]
logger = logging.getLogger(__name__)


class BaseParser(ABC):

    @staticmethod
    @abstractmethod
    def process_url(dmm, text: str, retries=5):
        raise NotImplementedError
