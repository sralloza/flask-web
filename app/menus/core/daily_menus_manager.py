import logging
import re
from datetime import date
from threading import Lock
from typing import List, Union

from app.menus.core.parser import Parsers
from app.menus.core.utils import get_menus_urls
from app.menus.models import DailyMenuDB, UpdateControl
from app.utils import now
from .structure import DailyMenu, Meal

logger = logging.getLogger(__name__)
M = Union[DailyMenu, List[DailyMenu]]


class DailyMenusManager:
    """Represents a controller of a list of menus."""

    def __init__(self):
        self.menus = []
        self._lock = Lock()

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __len__(self):
        return len(self.menus)

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
        """Sorts menus by date."""
        logger.debug('Sorting menus')
        self.menus.sort(key=lambda x: x.date, reverse=True)

    def to_string(self):
        """Returns string representation of the menus."""
        return '\n'.join([x.to_string() for x in self.menus])

    def to_html(self):
        """Returns html representation of the menus."""
        return '<br>'.join([x.to_html() for x in self.menus])

    def add_to_menus(self, menus: M):
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
    def load(cls, force=False):
        """Loads the menus, from the database and from the menus web server.

        Args:
            force (bool): if True, download menus from the web server even if today is
                in the database. Defaults to False.
        """

        self = DailyMenusManager()
        self.load_from_database()

        today_date = now().date()

        if today_date not in self or force:
            urls = get_menus_urls()

            for url in urls:
                Parsers.parse(url, self)

            Parsers.join()
            self.save_to_database()

        self.sort()
        return self

    @classmethod
    def add_manual(cls):
        self = cls()
        daily_menu = self._add_manual()
        self.add_to_menus(daily_menu)
        self.save_to_database()

    @classmethod
    def _add_manual(cls):
        while True:
            try:
                day = int(input('Day: '))
                month = int(input('Month: '))
                year = int(input('Year: '))
                lunch_p1 = input('Lunch p1: ')
                lunch_p2 = input('Lunch p2: ')
                dinner_p1 = input('Dinner p1: ')
                dinner_p2 = input('Dinner p2: ')
                lunch = Meal(lunch_p1, lunch_p2)
                dinner = Meal(dinner_p1, dinner_p2)

                dm = DailyMenu(day=day, month=month, year=year, lunch=lunch, dinner=dinner)

                if cls._confirm('Is correct %r?' % dm):
                    print('Saving...')
                    return dm

                print('Restarting...\n')
            except Exception as exc:
                print('%s: %s' % (exc.__class__.__name__, ', '.join(exc.args)))

    @staticmethod
    def _confirm(mesage: str) -> bool:
        mesage = mesage.strip() + ' [y/n/q]\t'
        while True:
            query = input(mesage)
            response = query[0].lower()

            if query == '' or response not in ['y', 'n', '1', '0', 's', 'q']:
                print('Invalid response')
            elif response == 'q':
                print('Cancelled')
                exit(0)
            else:
                return response in ['y', '1', 's']

    def to_json(self):
        """Returns the json representation of the menus."""

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
        """Loads the menus from the database."""
        logger.debug('Loading from database')
        self.add_to_menus([x.to_normal_daily_menu() for x in DailyMenuDB.query.all()])

    def save_to_database(self):
        """Saves the menus from the database (only if UpdateControl authorizes it)."""

        if not UpdateControl.should_update():
            logger.info('Permission denied by UpdateControl (%s)', UpdateControl.get_last_update())
            return self

        logger.debug('Saving menus to database')
        for menu in self:
            menu.to_database()
