import logging
import re
from datetime import datetime, date
from threading import Lock

import requests
from bs4 import BeautifulSoup as Soup

from app.menus.models import DailyMenuDB, UpdateControl
from .structure import _Index, DailyMenu
from .utils import get_menus_urls, filter_data, has_day, Patterns, Worker

logger = logging.getLogger(__name__)


class DailyMenusManager:
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
            if isinstance(menus, DailyMenu):
                self.menus.append(menus)
                return

            foo = {x.date: x for x in self.menus}
            for menu in menus:
                foo[menu.date] = menu

            self.menus += list(foo.values())

    @classmethod
    def load(cls, force=False):
        self = DailyMenusManager.__new__(cls)
        self.__init__()
        self.load_from_database()

        today = datetime.today().date()
        if today not in self or force:
            self.load_from_menus_urls()
            self.save_to_database()

        self.sort()
        return self

    def to_json(self):
        output = []

        for menu in self:
            foo = {}
            day = re.search(r'\((\w+)\)', menu.format_date()).group(1).capitalize()
            foo["id"] = menu.id
            foo["day"] = f'{day} {menu.date.day}'
            foo["lunch"] = {"p1": menu.lunch.p1, "p2": menu.lunch.p2}
            foo["dinner"] = {"p1": menu.dinner.p1, "p2": menu.dinner.p2}
            output.append(foo)

        return output

    def load_from_database(self):
        logger.debug('Loading from database')
        self.add_to_menus([x.to_normal_daily_menu() for x in DailyMenuDB.query.all()])

    def save_to_database(self):
        if not UpdateControl.should_update():
            logger.info('Permission denied by UpdateControl (%s)', UpdateControl.get_last_update())
            return

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

        s = Soup(r.text, 'html.parser')
        container = s.find('article', {'class': 'j-blog'})
        container = self.patch_urls(url, container.text)
        text = '\n'.join(x.strip() for x in container.splitlines() if x.strip())
        text = Patterns.fix_dates_pattern_1.sub(r'\1 \2', text)
        text = Patterns.fix_dates_pattern_2.sub(r'\1 \2', text)
        texts = [x.strip() for x in text.splitlines() if x.strip()]

        texts = filter_data(texts)
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
            if Patterns.day_pattern.search(text) is not None:
                if index.commit():
                    self._update_menu(index)

                index.reset()
                search = Patterns.day_pattern.search(text)

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
                for pattern in Patterns.ignore_patters:
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
