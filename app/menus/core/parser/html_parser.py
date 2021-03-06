"""Parser for html-like data."""
import logging
from datetime import date, datetime
from threading import Lock
from typing import Iterable, List, Union

from bs4 import BeautifulSoup as Soup

from app.menus.core.structure import DailyMenu, Index
from app.menus.core.utils import Patterns, filter_data, has_day
from app.utils import Translator

from .abc import BaseParser

logger = logging.getLogger(__name__)
_M = Union[DailyMenu, Iterable[DailyMenu]]
_ML = List[DailyMenu]
_S = List[str]


class HtmlParser(BaseParser):
    """Represents a controller of a list of menus."""

    _lock = Lock()

    @classmethod
    def process_text(cls, dmm, text: str, url: str):
        soup = Soup(text, "html.parser")
        container = soup.find("article", {"class": "j-blog"})
        text = "\n".join(x.strip() for x in container.text.splitlines() if x.strip())
        text = Patterns.fix_dates_pattern_1.sub(r"\1 \2", text)
        text = Patterns.fix_dates_pattern_2.sub(r"\1 \2", text)
        text = Patterns.fix_dates_pattern_3.sub(r"día: \1 de \2 de \3 (\4)", text)
        text = Patterns.fix_content_pattern_1.sub(r"\1 \2", text)
        text = Patterns.fix_content_pattern_2.sub(r" ", text)
        text = Patterns.fix_content_pattern_3.sub(r"\1\n\2", text)
        texts = [x.strip() for x in text.splitlines() if x.strip()]

        texts = filter_data(texts)
        menus = [DailyMenu.from_datetime(x) for x in texts if has_day(x)]
        assert menus

        HtmlParser._process_texts(texts, menus)
        for menu in menus:
            menu.url = url
        dmm.add_to_menus(menus)

    @staticmethod
    def _process_texts(texts: _S, menus: _ML):
        """Processes texts retrieved from url."""
        logger.debug("Processing texts")
        index = Index()
        for text in texts:
            text = text.replace("_", " ").lower()  # .strip()
            if Patterns.day_pattern.search(text) is not None:
                if index.commit():
                    HtmlParser._update_menu(index, menus)

                index.reset()
                search = Patterns.day_pattern.search(text)

                day = int(search.group("day"))
                month = search.group("month")
                month = datetime.strptime(
                    Translator.spanish_to_english(month.lower()), "%B"
                ).month
                year = int(search.group("year"))

                index.set_date(date(year, month, day))
                continue

            if "combinado" in text:
                _filtered = text.replace("1er plato", "")
                if len(_filtered) - len("plato combinado") > 3:
                    index.set_combined(index.state)
                    index.set_first("PC: " + text.split(":")[-1].strip())
                    continue
                text = "plato combinado"
            elif ("coctel" in text or "cóctel" in text) and len(text.split()) < 3:
                index.set_first("cóctel")
                continue

            if Patterns.pattern_lunch.search(text):
                index.set_state("LUNCH")
            elif Patterns.pattern_dinner.search(text):
                index.set_state("DINNER")
            elif "1er" in text:
                index.set_first(text.split(":")[1])
            elif "2º" in text:
                index.set_second(text.split(":")[1])
            else:
                index.decide(text)

        if index.commit():
            HtmlParser._update_menu(index, menus)

        return menus

    @staticmethod
    def _update_menu(index: Index, menus: _ML):
        # logger.debug('Updating menu')
        with HtmlParser._lock:
            for i, _ in enumerate(menus):
                if menus[i].date == index.date:
                    if index.is_combinated:
                        menus[i].set_combined(index.meal_combined)

                    index_info = index.to_dict()
                    index_info.pop("day", None)
                    index_info.pop("month", None)
                    index_info.pop("year", None)
                    index_info.pop("date", None)
                    index_info.pop("weekday", None)

                    menus[i].update(**index_info)
                    break
