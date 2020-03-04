import logging
from collections import UserList
from threading import Lock, Thread

from app.menus.core.exceptions import ParserError
from app.menus.core.parser.abc import BaseParser
from app.menus.core.parser.html_parser import HtmlParser
from app.menus.core.parser.manual_parser import ManualParser
from app.utils.exceptions import DownloaderError
from app.utils.networking import downloader

logger = logging.getLogger(__name__)

KNOWN_UNPARSEABLE_URLS = (
    "https://www.residenciasantiago.es/2018/06/18/19-06-2018/",
    "https://www.residenciasantiago.es/2018/05/21/22-05-2018-al-28-05-2018/",
    "https://www.residenciasantiago.es/2018/03/19/semana-del-20-al-26-de-marzo-2018/",
)


class ParserThread(Thread):
    """Thread made to control."""

    def __init__(self, url, dmm):
        super().__init__()
        self.url = url
        self.dmm = dmm

    def run(self):
        logger.debug("Starting %s with url %r", self.name, self.url)

        if self.url in KNOWN_UNPARSEABLE_URLS:
            logger.warning("Skipped url because its in KNOWN_UNPARSEABLE_URLS")
            return

        try:
            response = downloader.get(self.url)
        except DownloaderError as exc:
            logger.error("Fatal connection error downloading %s", self.url)
            raise DownloaderError(
                "Fatal connection error downloading %s" % self.url
            ) from exc

        for parser in Parsers.parsers:
            try:
                logger.debug("Trying with parser %r", parser.__name__)
                parser.process_text(dmm=self.dmm, text=response.text, url=self.url)
                logger.info("URL parsed correcty with parser %r", parser.__name__)
                return
            except:
                logger.exception(
                    "Exception parsing %r using parser %r:", self.url, parser.__name__
                )
                continue

        logger.error("None of the parsers could parse url %r", self.url)
        raise ParserError("None of the parsers could parse url %r" % self.url)


class ParserThreadList(UserList):
    """Custom list to store parser threads."""

    def append(self, something: ParserThread):
        if not isinstance(something, ParserThread):
            raise TypeError(
                "ParserThreadList can only contain ParserThread instances, not %r"
                % type(ParserThread).__name__,
            )

        super(ParserThreadList, self).append(something)


class Parsers:
    """Parsers manager class."""

    parsers = [HtmlParser, ManualParser]
    _threads = ParserThreadList()
    _lock = Lock()

    @staticmethod
    def _append(thread: ParserThread):
        """Appends a thread to the list of threads.

        Args:
            thread (ParserThread): thread to append.
        """
        with Parsers._lock:
            Parsers._threads.append(thread)

    @staticmethod
    def parse(url, dmm):
        """Starts the parsing of the url.

        Args:
            url (str): url to get the menus from.
            dmm (DailyMenusManager): DMM instance.
        """
        worker = ParserThread(url, dmm)
        worker.start()
        Parsers._append(worker)

    @staticmethod
    def join():
        """Waits for all parser threads to finish."""
        for worker in Parsers._threads:
            worker.join()

        logger.debug("Threads finished")
