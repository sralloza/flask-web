"""Parser for non-html data."""
from bs4 import BeautifulSoup

from app.menus.core.exceptions import ParserError
from app.menus.core.parser import BaseParser


class ManualParser(BaseParser):
    def __init__(self, soup):
        """Parser for non-html data.

        Args:
            soup (bs4.BeautifulSoup): text parsed by `bs4.BeautifulSoup`.
        """
        self.soup = soup

    @classmethod
    def process_text(cls, dmm, text: str, url: str):
        soup = BeautifulSoup(text, "html.parser")

        self = cls(soup)

        if self.detect_if_pdf():
            return True

        if self.detect_if_photo():
            return True

        raise ParserError

    def detect_if_pdf(self):
        """Detects if menus data is in pdf format.

        Returns:
            bool: True if menus data is in pdf format, False otherwise.
        """
        try:
            pdf = self.soup.find("div", class_="cc-m-download-file-link").a["href"]
            return pdf is not None
        except AttributeError:
            return False

    def detect_if_photo(self):
        """Detects if menus data is in photo format.

        Returns:
            bool: True if menus data is in photo format, False otherwise.
        """
        container = self.soup.find("div", class_="post j-blog-content")
        photo = container.find("img", alt="")
        return photo is not None
