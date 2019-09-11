import logging
from datetime import date, datetime
from threading import Lock
from typing import Union, Iterable, List

from bs4 import BeautifulSoup as Soup

from app.menus.core.structure import DailyMenu, Index
from app.menus.core.utils import Patterns, filter_data, has_day
from .abc import BaseParser

logger = logging.getLogger(__name__)
M = Union[DailyMenu, Iterable[DailyMenu]]
ML = List[DailyMenu]
S = List[str]


class HtmlParser(BaseParser):
    """Represents a controller of a list of menus."""
    _lock = Lock()

    @staticmethod
    def process_url(dmm, text: str, retries=5):
        """Processes url in search from menus."""
        s = Soup(text, 'html.parser')
        container = s.find('article', {'class': 'j-blog'})
        text = '\n'.join(x.strip() for x in container.text.splitlines() if x.strip())
        text = Patterns.fix_dates_pattern_1.sub(r'\1 \2', text)
        text = Patterns.fix_dates_pattern_2.sub(r'\1 \2', text)
        texts = [x.strip() for x in text.splitlines() if x.strip()]

        texts = filter_data(texts)
        menus = [DailyMenu.from_datetime(x) for x in texts if has_day(x)]
        assert menus

        HtmlParser._process_texts(texts, menus)
        dmm.add_to_menus(menus)

    @staticmethod
    def _process_texts(texts: S, menus: ML):
        """Processes texts retrieved from url."""
        logger.debug('Processing texts')
        index = Index()
        for text in texts:
            text = text.replace('_', ' ').lower()
            if Patterns.day_pattern.search(text) is not None:
                if index.commit():
                    HtmlParser._update_menu(index, menus)

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
            HtmlParser._update_menu(index, menus)

        return menus

    @staticmethod
    def _update_menu(index: Index, menus: ML):
        # logger.debug('Updating menu')
        with HtmlParser._lock:
            for i, menu in enumerate(menus):
                if menus[i].date == index.date:
                    if index.is_combinated:
                        menus[i].set_combined(index.meal_combined)

                    index_info = index.to_dict()
                    index_info.pop('day', None)
                    index_info.pop('month', None)
                    index_info.pop('year', None)
                    index_info.pop('date', None)
                    index_info.pop('weekday', None)

                    menus[i].update(**index_info)
                    break
