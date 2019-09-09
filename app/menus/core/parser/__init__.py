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
