import logging
from collections import UserList
from threading import Thread, Lock

import requests

from app.menus.core.exceptions import ParserError
from app.menus.core.parser.abc import BaseParser
from app.menus.core.parser.html_parser import HtmlParser
from app.menus.core.parser.manual_parser import ManualParser

logger = logging.getLogger(__name__)


class ParserThread(Thread):
    """Thread made to control."""

    def __init__(self, url, dmm, retries=5):
        super().__init__()
        self.url = url
        self.dmm = dmm
        self.retries = retries

    def run(self):
        logger.debug("Starting %s with url %r", type(self).__name__, self.url)

        retries_left = self.retries
        while retries_left:
            try:
                response = requests.get(self.url)
                break
            except Exception:
                retries_left -= 1
                if not retries_left:
                    logger.error("Fatal connection error downloading %s", self.url)
                    raise requests.exceptions.ConnectionError(
                        "Fatal connection error downloading %s" % self.url
                    )

        for parser in Parsers.parsers:
            try:
                logger.debug("Trying with parser %r", parser.__name__)
                parser.process_text(dmm=self.dmm, text=response.text)
                logger.info("URL parsed correcty with parser %r", parser.__name__)
                return
            except Exception:
                logger.exception("Exception using parser %r:", parser.__name__)
                continue

        logger.error("None of the parsers could parse url %r", self.url)
        raise ParserError("None of the parsers could parse url %r" % self.url)


class ParserThreadList(UserList):
    def append(self, object: ParserThread):
        if not isinstance(object, ParserThread):
            raise TypeError(
                "ParserThreadList can only contain ParserThread instances, not %r",
                type(ParserThread).__name__,
            )

        super(ParserThreadList, self).append(object)


class Parsers:
    parsers = [HtmlParser, ManualParser]
    _threads = ParserThreadList()
    _lock = Lock()

    @staticmethod
    def _append(thread: ParserThread):
        with Parsers._lock:
            Parsers._threads.append(thread)

    @staticmethod
    def parse(url, dmm, retries=5):
        worker = ParserThread(url, dmm, retries)
        worker.start()
        Parsers._append(worker)

    @staticmethod
    def join():
        for worker in Parsers._threads:
            worker.join()

        logger.debug("Threads finished")
