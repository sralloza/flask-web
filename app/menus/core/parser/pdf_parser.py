import requests
from bs4 import BeautifulSoup

from app.config import Config
from .abc import BaseParser, BaseWorker


class PdfParser(BaseParser):
    @staticmethod
    def process_url(dmm, url: str, retries=5):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        pdf_link = soup.find('div', class_='cc-m-download-file-link').a['href']

        pdf_link = Config.BASE_RESIDENCE_URL + pdf_link

        pdf_byets = requests.get(pdf_link).content


class PdfParserWorker(BaseWorker):
    pass
