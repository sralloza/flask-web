import logging
from threading import Thread, Lock
from typing import List, Type

import requests

from app.menus.core.exceptions import ParserError
from app.menus.core.parser.abc import BaseParser
from app.menus.core.parser.html_parser import HtmlParser, HtmlParserWorker
from app.menus.core.parser.pdf_parser import PdfParser, PdfParserWorker

logger = logging.getLogger(__name__)
P = List[Type[BaseParser]]

worker_map = {HtmlParser: HtmlParserWorker, PdfParser: PdfParserWorker}


class Parsers:
    _parsers = [HtmlParser, PdfParser]
    _workers = []
    _lock = Lock()

    @staticmethod
    def parse(url, dmm, retries=5):
        worker = BossWorker(url, dmm, retries)
        worker.start()
        Parsers._append(worker)

    @staticmethod
    def _append(worker):
        assert isinstance(worker, BossWorker)
        with Parsers._lock:
            Parsers._workers.append(worker)

    @staticmethod
    def join():
        for worker in Parsers._workers:
            worker.join()

        logger.debug('Workers finished')


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
                logger.debug('Trying with parser %r', parser.__name__)
                parser.process_url(dmm=self.dmm, text=response.text, retries=self.retries)
                logger.info('URL parsed correcty with parser %r', parser.__name__)
                return
            except Exception:
                logger.exception('Exception using parser %r:', parser.__name__)
                continue

        raise ParserError('None of the parsers could parse url %r' % self.url)
