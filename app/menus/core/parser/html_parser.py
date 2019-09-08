import logging
from datetime import date, datetime
from threading import Lock
from typing import Union, Iterable

import requests
from bs4 import BeautifulSoup as Soup

from app.menus.core.parser import BaseParser
from app.menus.core.structure import DailyMenu, Index
from app.menus.core.utils import get_menus_urls, Worker, Patterns, filter_data, has_day

logger = logging.getLogger(__name__)
M = Union[DailyMenu, Iterable[DailyMenu]]


class HtmlParser(BaseParser):
    """Represents a controller of a list of menus."""

    def __init__(self, dmm):
        super().__init__(dmm)
        self.menus = []
        self._lock = Lock()

    def save_menu(self, menus: M):
        """Adds menus to the database.

        Args:
            menus: menus to add.

        """

        with self._lock:
            if isinstance(menus, DailyMenu):
                menus = [menus, ]

            existing_dates = [x.date for x in self.menus]
            new_menus = []
            for menu in menus:
                if menu.date not in existing_dates:
                    new_menus.append(menu)

            self.menus += new_menus

    @classmethod
    def load(cls, dmm):
        """Loads menus from menus urls."""

        self = HtmlParser(dmm=dmm)
        logger.debug('Loading from menus urls')
        threads = []
        for u in get_menus_urls():
            t = Worker(u, self)
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        self.dmm.add_to_menus(self.menus)

    def process_url(self, url, retries=5):
        """Processes url in search from menus."""
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
        text = '\n'.join(x.strip() for x in container.text.splitlines() if x.strip())
        text = Patterns.fix_dates_pattern_1.sub(r'\1 \2', text)
        text = Patterns.fix_dates_pattern_2.sub(r'\1 \2', text)
        texts = [x.strip() for x in text.splitlines() if x.strip()]

        texts = filter_data(texts)
        menus = [DailyMenu.from_datetime(x) for x in texts if has_day(x)]

        self.save_menu(menus)
        self._process_texts(texts)

        return self

    def _process_texts(self, texts):
        """Processes texts retrieved from url."""
        logger.debug('Processing texts')
        index = Index()
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

    def _update_menu(self, index: Index):
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
