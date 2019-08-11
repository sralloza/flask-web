import logging
import re
from datetime import datetime, date
from threading import Lock, Thread

import requests
from bs4 import BeautifulSoup as Soup

from app.menus.models import DailyMenu as DailyMenuDB
from .get_urls import get_menus_urls
from .structure import DailyMenu, _Index

logger = logging.getLogger()


def has_day(x):
    x = x.lower()

    return Patterns.day_pattern.search(x) is not None


def filter_data(data):
    while '' in data:
        data.remove('')

    for i in range(len(data)):
        data[i] = data[i].lower().strip()

    out = []
    for i, d in enumerate(data):
        if '1er plato:' in d:
            out.append(d)
        elif '2º plato:' in d:
            if 'combinado' in data[i - 1]:
                d = d.replace('2º plato:', '').strip()
                out[-1] += ' ' + d
                continue
            out.append(d)
        elif 'comida' in d:
            out.append(d)
        elif 'cena' in d:
            out.append(d)
        elif 'cóctel' in d or 'coctel' in d:
            out.append('cóctel')
        elif 'combinado' in d:
            out.append(d.replace('1er plato:', '').strip())
        elif Patterns.day_pattern.search(d) is not None:
            out.append(Patterns.day_pattern.search(d).group())
        elif Patterns.semi_day_pattern_2.search(d) is not None:
            if Patterns.semi_day_pattern_1.search(data[i - 1]) is not None:
                foo = Patterns.semi_day_pattern_1.search(data[i - 1]).group() + ' de ' + \
                      Patterns.semi_day_pattern_2.search(d).group()
                out.append(foo)
        else:
            if 'combinado' in data[i - 1] and 'postre' not in d:
                out[-1] += ' ' + d
    return out


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
