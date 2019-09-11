import logging
from typing import List, Type

from app.menus.core.exceptions import ParserError
from app.menus.core.parser.abc import BaseParser
from app.menus.core.parser.html_parser import HtmlParser
from app.menus.core.parser.pdf_parser import PdfParser

logger = logging.getLogger(__name__)
P = List[Type[BaseParser]]


class Parsers:
    parsers = [HtmlParser, PdfParser]

    @staticmethod
    def parse(url, dmm, retries=5):
        for parser in Parsers.parsers:
            try:
                parser.process_url(dmm, url, retries=retries)
                return
            except Exception:
                logger.exception('Exception using parser %r:', type(parser).__name__)
                continue

        raise ParserError('None of the parsers could parse url %r' % url)

    @staticmethod
    def _parse(url, dmm, retries=5):
        for parser in Parsers.parsers:

class BossWorker(Thread):
    """Thread made to control."""

    def __init__(self, url, dmm, retries=5):
        super().__init__()
        self.url = url
        self.dmm = dmm
        self.retries = retries

    def run(self):
        logger.debug('Starting %s with url %r', type(self).__name__, self.url)
        response = requests.get(self.url)

        for parser in Parsers._parsers:
            try:
                parser.process_url(dmm=self.dmm, text=response.text, retries=self.retries)
                return
            except Exception:
                logger.exception('Exception using parser %r:', type(parser).__name__)
                continue

        raise ParserError('None of the parsers could parse url %r' % self.url)
