import logging
import re
from datetime import datetime, date
from threading import Lock, Thread

import requests
from bs4 import BeautifulSoup as Soup

from app.new_menus.models import DailyMenu as DailyMenuDB
from .get_urls import get_menus_urls
from .structure import DailyMenu, _Index

# TODO get menus url

logger = logging.getLogger()


class Functions:
    @staticmethod
    def has_day(x):
        x = x.lower()

        return DailyMenusManager._day_pattern.search(x) is not None

    @staticmethod
    def filter_data(x):
        x = x.lower()
        if not x:
            return False
        if 'buffet' in x:
            return False
        if 'mantequilla' in x:
            return False
        if 'tumaca' in x:
            return False
        if 'desayuno' in x:
            return False
        if 'postre' in x:
            return False
        if 'tag' in x:
            return False
        for pattern in DailyMenusManager.ignore_patters:
            if pattern.search(x) is not None:
                return False
        return True


class DailyMenusManager:
    _day_pattern = re.compile(
        r'día: (?P<day>\d+) de (?P<month>\w+) de (?P<year>\d{4}) \((?P<weekday>\w+)\)',
        re.IGNORECASE)

    _fix_dates_pattern = re.compile(r'(\w+)\n(\d{4})', re.I)

    ignore_patters = (
        re.compile(r'\d+\.\s\w+\s\d+', re.IGNORECASE),
        re.compile(r'semana del \d+ al \d+ de \w+', re.IGNORECASE),
        re.compile(r'semana del \d+ de \w+ al \d+ de \w+ \d+', re.IGNORECASE)
    )

    def __init__(self):
        self.menus = []
        self._lock = Lock()

    def __str__(self):
        return '\n'.join([repr(x) for x in self.menus])

    def __contains__(self, item: date):
        if not isinstance(item, date):
            raise TypeError(f'Contains does only work with dates, not {type(item).__name__}')

        return item in (x.date for x in self.menus)

    def __iter__(self):
        return iter(self.menus)

    def sort(self):
        logger.debug('Sorting menus')
        self.menus.sort(key=lambda x: x.date)

    def to_string(self):
        return '\n'.join([x.to_string() for x in self.menus])

    def to_html(self):
        return '<br>'.join([x.to_html() for x in self.menus])

    def add_to_menus(self, menus):
        with self._lock:
            try:
                self.menus += menus
            except TypeError:
                self.menus += [menus, ]

    @classmethod
    def load(cls):
        self = DailyMenusManager.__new__(cls)
        self.__init__()
        self.load_from_database()

        today = datetime.today().date()
        if today not in self:
            self.load_from_menus_urls()
            self.save_to_database()

        self.sort()
        return self

    def load_from_database(self):
        logger.debug('Loading from database')
        self.add_to_menus([x.to_normal_daily_menu() for x in DailyMenuDB.query.all()])

    def save_to_database(self):
        logger.debug('Saving menus to database')
        for menu in self:
            menu.to_database()

    def load_from_menus_urls(self):
        logger.debug('Loading from menus urls')
        threads = []
        for u in get_menus_urls():
            t = Worker(u, self)
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

    def process_url(self, url, retries=5):
        logger.debug('Processing url %r', url)
        r = None
        while retries:
            try:
                r = requests.get(url)
                break
            except ConnectionError:
                retries -= 1

        if not retries:
            return -1

        s = Soup(r.content, 'html.parser')
        container = s.find('article', {'class': 'j-blog'})
        text = '\n'.join(x.strip() for x in container.text.splitlines() if x.strip())

        text = self._fix_dates_pattern.sub(r'\g<1> \g<2>', text)
        texts = [x.strip() for x in text.splitlines() if x.strip()]

        texts = [x for x in texts if Functions.filter_data(x)]
        menus = [DailyMenu.from_datetime(x) for x in texts if Functions.has_day(x)]

        self.add_to_menus(menus)
        self._process_texts(texts)

        return self

    def _process_texts(self, texts):
        logger.debug('Processing texts')
        index = _Index()
        for text in texts:
            text = text.replace('_', ' ').lower()
            if self._day_pattern.search(text) is not None:
                if index.commit():
                    self._update_menu(index)

                index.reset()
                search = self._day_pattern.search(text)

                day = int(search.group('day'))
                month = search.group('month')
                month = datetime.strptime(DailyMenu.s_to_e(month.lower()), '%B').month
                year = int(search.group('year'))

                index.set_date(date(year, month, day))

            elif 'comida' in text:
                index.set_state('LUNCH')
            elif 'cena' in text:
                index.set_state('DINNER')
            elif '1er' in text:
                index.set_first(text.split(':')[1])
            elif '2º' in text:
                index.set_second(text.split(':')[1])
            else:
                for pattern in self.ignore_patters:
                    if pattern.search(text) is not None:
                        break
                else:
                    index.decide(text)

        if index.commit():
            self._update_menu(index)

    def _update_menu(self, index: _Index):
        logger.debug('Updating menu')
        with self._lock:
            for i, menu in enumerate(self.menus):
                if self.menus[i].date == index.date:
                    index_info = index.to_dict()
                    index_info.pop('day', None)
                    index_info.pop('month', None)
                    index_info.pop('year', None)
                    index_info.pop('date', None)
                    index_info.pop('weekday', None)

                    self.menus[i].update(**index_info)
                    break


class Worker(Thread):
    def __init__(self, url, dmm_instance: DailyMenusManager, retries=5):
        super().__init__()
        self.url = url
        self.retries = retries
        self.dmm = dmm_instance

    def run(self):
        logger.debug('Starting worker')
        self.dmm.process_url(self.url, self.retries)
