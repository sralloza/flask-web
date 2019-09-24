import logging
from abc import ABC, abstractmethod
from typing import List

S = List[str]
logger = logging.getLogger(__name__)


class BaseParser(ABC):

    @classmethod
    @abstractmethod
    def process_text(cls, dmm, text: str, retries=5):
        raise NotImplementedError
