from bs4 import BeautifulSoup

from app.menus.core.exceptions import ParserError
from app.menus.core.parser import BaseParser


class ManualParser(BaseParser):
    def __init__(self, soup):
        self.soup = soup

    @classmethod
    def process_text(cls, dmm, text: str):
        soup = BeautifulSoup(text, 'html.parser')

        self = cls(soup)

        if self.detect_if_pdf():
            return True

        if self.detect_if_photo():
            return True

        raise ParserError

    def detect_if_pdf(self):
        try:
            pdf = self.soup.find('div', class_='cc-m-download-file-link').a['href']
            return pdf is not None
        except AttributeError:
            return False

    def detect_if_photo(self):
        container = self.soup.find('div', class_='post j-blog-content')
        photo = container.find('img', alt='')
        return photo is not None