import logging
import re
from threading import Thread

from app.menus.core.daily_menus_manager import DailyMenusManager
from .structure import DailyMenu, _Index

logger = logging.getLogger()


class Patterns:
    day_pattern = re.compile(
        r'día: (?P<day>\d+) de (?P<month>\w+) de (?P<year>\d{4})\s?\((?P<weekday>\w+)\)',
        re.IGNORECASE)

    semi_day_pattern_1 = re.compile(r'día: (?P<day>\d+) de (?P<month>\w+)$', re.I)
    semi_day_pattern_2 = re.compile(r'(?P<year>\d{4})\s?\((?P<weekday>\w+)\)', re.I)

    fix_dates_pattern_1 = re.compile(r'(\w+)\n(\d{4})', re.I)
    fix_dates_pattern_2 = re.compile(r'(día:)[\s\n]+(\d+)', re.I)

    ignore_patters = (
        re.compile(r'\d+\.\s\w+\s\d+', re.IGNORECASE),
        re.compile(r'semana del \d+ al \d+ de \w+', re.IGNORECASE),
        re.compile(r'semana del \d+ de \w+ al \d+ de \w+ \d+', re.IGNORECASE)
    )


class Worker(Thread):
    def __init__(self, url, dmm_instance: DailyMenusManager, retries=5):
        super().__init__()
        self.url = url
        self.retries = retries
        self.dmm = dmm_instance

    def run(self):
        logger.debug('Starting worker with url %s', self.url)
        self.dmm.process_url(self.url, self.retries)
