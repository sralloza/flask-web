"""Abstract bases for Parsers."""
import logging
from abc import ABC, abstractmethod
from typing import List

S = List[str]
logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Abstract class for Parsers."""
    @classmethod
    @abstractmethod
    def process_text(cls, dmm, text: str, url: str):
        """Process the text previously downloaded from url generating
        a set of instances of DailyMenu, which links to dmm.

        Args:
            dmm (DailyMenusManager): DMM instance to link the menus to.
            text (str): texts downloaded from url.
            url (str): url from which the menus were downloaded.
        """
        raise NotImplementedError
