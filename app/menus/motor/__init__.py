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

    return DailyMenusManager.day_pattern.search(x) is not None


def filter_data_2(data):
    while '' in data:
        data.remove('')

    for i in range(len(data)):
        data[i] = data[i].lower().strip()

    out = []
    for i, d in enumerate(data):
        if '1er plato:' in d:
            out.append(d)
        elif '2º plato:' in d:
            out.append(d)
        elif 'comida' in d:
            out.append(d)
        elif 'cena' in d:
            out.append(d)
        elif 'cóctel' in d or 'coctel' in d:
            out.append('cóctel')
        elif 'combinado' in d:
            out.append(d.replace('1er plato:', '').strip())
        elif DailyMenusManager.day_pattern.search(d) is not None:
            out.append(DailyMenusManager.day_pattern.search(d).group())
        else:
            if 'combinado' in data[i - 1]:
                out[-1] += ' ' + d
    return out


def filter_data(x):
    x = x.lower()
    if not x:
        return ''
    if '1er plato' in x:
        return x
    if '1 er plato' in x:
        return x.replace('1 er', '1er')
    if '2º plato' in x:
        return x
    if '2 º plato' in x:
        return x.replace('2 º', '2º')
    if 'comida:' in x:
        return x
    if 'cena:' in x:
        return x
    if 'combinado' in x:
        return x
    if DailyMenusManager.day_pattern.search(x) is not None:
        return DailyMenusManager.day_pattern.search(x).group()
    return ''


class DailyMenusManager:
    day_pattern = re.compile(
        r'día: (?P<day>\d+) de (?P<month>\w+) de (?P<year>\d{4})\s?\((?P<weekday>\w+)\)',
        re.IGNORECASE)

    fix_dates_pattern = re.compile(r'(\w+)\n(\d{4})', re.I)

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

    def __getitem__(self, item):
        if not isinstance(item, date):
            raise TypeError(f'Getitem does only work with dates, not {type(item).__name__}')

        for menu in self.menus:
            if menu.date == item:
                return menu

        raise KeyError(f'No menu found: {item}')

    def sort(self):
        logger.debug('Sorting menus')
        self.menus.sort(key=lambda x: x.date, reverse=True)

    def to_string(self):
        return '\n'.join([x.to_string() for x in self.menus])

    def to_html(self):
        return '<br>'.join([x.to_html() for x in self.menus])

    def add_to_menus(self, menus):
        with self._lock:
            foo = {x.date: x for x in self.menus}
            for menu in menus:
                foo[menu.date] = menu

            self.menus = list(foo.values())

    @classmethod
    def load(cls, force=False, index_path=None):
        self = DailyMenusManager.__new__(cls)
        self.__init__()
        self.load_from_database()

        today = datetime.today().date()
        if today not in self or force:
            self.load_from_menus_urls(index_path)
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

    def load_from_menus_urls(self, index_path=None):
        logger.debug('Loading from menus urls')
        threads = []
        for u in get_menus_urls(index_path=index_path):
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
        container = self.patch_urls(url, container.text)
        text = '\n'.join(x.strip() for x in container.splitlines() if x.strip())
        text = self.fix_dates_pattern.sub(r'\g<1> \g<2>', text)
        texts = [x.strip() for x in text.splitlines() if x.strip()]

        texts = filter_data_2(texts)
        menus = [DailyMenu.from_datetime(x) for x in texts if has_day(x)]

        self.add_to_menus(menus)
        self._process_texts(texts)

        return self

    @staticmethod
    def patch_urls(url, text):
        if url != 'https://www.residenciasantiago.es/2019/04/01/semana-del-2-al-8-de-abril-2019/':
            return text
        text = text.replace('06 DE MARZO DE 2019', '06 DE ABRIL DE 2019')
        text = text.replace('07 DE MARZO DE 2019', '07 DE ABRIL DE 2019')
        text = text.replace('1ER PLATO:\n\n\nBARBACOA', '1ER PLATO: BARBACOA')
        return text

    def _process_texts(self, texts):
        logger.debug('Processing texts')
        index = _Index()
        for text in texts:
            text = text.replace('_', ' ').lower()
            if self.day_pattern.search(text) is not None:
                if index.commit():
                    self._update_menu(index)

                index.reset()
                search = self.day_pattern.search(text)

                day = int(search.group('day'))
                month = search.group('month')
                month = datetime.strptime(DailyMenu.s_to_e(month.lower()), '%B').month
                year = int(search.group('year'))

                index.set_date(date(year, month, day))
                continue

            if 'combinado' in text:
                index.set_combined(index.state)
                foo = text.split(':')[-1].strip()
                index.set_first('PC: ' + foo)
            elif 'coctel' in text or 'cóctel' in text:
                index.set_first('cóctel')
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
                    if index.is_combinated:
                        self.menus[i].set_combined(index.meal_combined)

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
        logger.debug('Starting worker with url %s', self.url)
        self.dmm.process_url(self.url, self.retries)
