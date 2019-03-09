import locale
import logging
import warnings
from datetime import datetime, date
from typing import Union

from sqlalchemy.exc import IntegrityError

from app.new_menus.models import DailyMenu as DailyMenuDB, db

locale.setlocale(locale.LC_ALL, 'spanish')
logger = logging.getLogger(__name__)


class MealError(Exception):
    """Meal error."""


class _Index:
    """Represents the interface to store temporal values of a DailyMenu."""
    _valid_states = ('LUNCH', 'DINNER')

    def __init__(self, lunch=None, dinner=None, dt=None, state=None):
        """
        Notes:
            All args in this class are meant to be changed dinamically. They are not meant to be
            declared (it is only for testing purposes).

        Args:
            lunch (Meal): lunch of the DailyMenu
            dinner (Meal: dinner of the DailyMenu
            dt (date): date of the DailyMenu
            state (str): current state of the _Index. Its valid states are declared in
                _Index._valid_states.
        """
        self._date = dt
        self._lunch = lunch or Meal()
        self._dinner = dinner or Meal()
        self._state = None

        if state:
            self.set_state(state)

    @property
    def lunch(self):
        return self._lunch

    @property
    def dinner(self):
        return self._dinner

    @property
    def meal_type(self):
        return self._state

    @property
    def date(self):
        return self._date

    def commit(self):
        """Decides if the _Index is ready to be stored in a database.
        The conditions are:
         - Have a date
         - Have a state
         - Have at least a non empty dinner or launch.
        """
        if not self._date:
            return False
        if not self._state:
            return False
        if not self._lunch.is_empty():
            return True
        if not self._dinner.is_empty():
            return True
        return False

    def reset(self):
        """Deletes all the temporal values of the _Index."""
        self.__init__()

    def set_date(self, new_date: date):
        """Sets a new date."""
        self._date = new_date

    def is_actual_meal_empty(self):
        if self._state == 'LUNCH':
            return self._lunch.is_empty()
        elif self._state == 'DINNER':
            return self._dinner.is_empty()
        elif self._state is None:
            raise MealError('Meal_type is None while checking for emtpyness')
        raise MealError(f'Invalid value for meal_type: {self._state}')

    def decide(self, text: str):
        if self.is_actual_meal_empty():
            return self.set_first(text)
        else:
            warnings.warn(f'Could not decide: {text}', stacklevel=2)

    def set_state(self, meal_type):
        if meal_type not in self._valid_states:
            raise ValueError('Invalid meal type: %s from %r'.format(meal_type, self._valid_states))
        self._state = meal_type

    def set_first(self, first):
        if not first:
            return

        if self._state == 'LUNCH':
            self._lunch.p1 = first
        elif self.meal_type == 'DINNER':
            self._dinner.p1 = first
        else:
            raise ValueError(f'Invalid meal type: {self._state}')

    def set_second(self, second):
        if not second:
            return

        if self._state == 'LUNCH':
            self._lunch.p2 = second
        elif self._state == 'DINNER':
            self._dinner.p2 = second
        else:
            raise ValueError(f'Invalid meal type: {self._state}')

    def to_dict(self):
        return {'lunch': self._lunch, 'dinner': self._dinner}


class Meal:
    def __init__(self, p1=None, p2=None):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return f'{self.p1} - {self.p2}'

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def is_empty(self):
        return self.p1 is None and self.p2 is None

    def update(self, **kwargs):
        self.p1 = self.p1 or kwargs.pop('p1', None)
        self.p2 = self.p2 or kwargs.pop('p2', None)

        if kwargs:
            raise ValueError(f'Invalid arguments: {kwargs}')


class DailyMenu:
    def __init__(self, day: int, month: int, year: int, lunch: Meal = None, dinner: Meal = None):
        self.day = day
        self.month = month
        self.year = year
        self.lunch = lunch or Meal()
        self.dinner = dinner or Meal()

        self.date = date(self.year, self.month, self.day)
        self.weekday = self.date.strftime('%A').capitalize()
        self.id = int(f'{self.year:04d}{self.month:02d}{self.day:02d}')

    def __eq__(self, other):
        return self.day == other.day and self.month == other.month and self.year == other.year \
               and self.lunch == other.lunch and self.dinner == other.dinner

    def __str__(self):
        return self.format_date()

    def __repr__(self):
        return str(self)

    def to_database(self):
        logger.debug('Saving menu %d to database', self.id)
        menu = DailyMenuDB(
            id=self.id, day=self.day, month=self.month, year=self.year, lunch1=self.lunch.p1,
            lunch2=self.lunch.p2, dinner1=self.dinner.p1, dinner2=self.dinner.p2)
        db.session.add(menu)
        try:
            db.session.commit()
            logger.info('Saved menu %d to database', self.id)
            return True
        except IntegrityError:
            logger.debug('Could not save menu %d to database (IntegrityError)', self.id)
            db.session.rollback()
            return False
        finally:
            db.session.close()

    def to_string(self):
        string = ''
        string += f'{self.format_date()}\n'

        if not self.lunch.is_empty():
            string += f' - Comida\n'
            string += f'   - {self.lunch.p1}\n'

            if self.lunch.p2:
                string += f'   - {self.lunch.p2}\n'

        if not self.dinner.is_empty():
            string += f' - Cena\n'
            string += f'   - {self.dinner.p1}\n'

            if self.dinner.p2:
                string += f'   - {self.dinner.p2}\n'

        return string

    def to_html(self):
        return self.to_string().replace('\n', '<br>')

    @classmethod
    def from_datetime(cls, dt: Union[datetime, str, date]):
        self = DailyMenu.__new__(DailyMenu)

        if isinstance(dt, str):
            dt = dt.lower()
            dt = dt.replace('miercoles', 'miércoles')
            dt = dt.replace('sabado', 'sábado')
            dt = datetime.strptime(dt, 'día: %d de %B de %Y (%A)')

        if not isinstance(dt, (datetime, date)):
            raise TypeError(f'dt must be datetime or str, not {type(dt).__name__}')

        self.__init__(dt.day, dt.month, dt.year)

        return self

    def format_date(self):
        return self.date.strftime('%d de %B de %Y (%A)')

    def update(self, **kwargs):
        lunch = kwargs.pop('lunch', None)
        dinner = kwargs.pop('dinner', None)

        if lunch:
            if isinstance(lunch, Meal) is False:
                raise ValueError('Lunch must be Meal')
            self.lunch = lunch

        if dinner:
            if isinstance(dinner, Meal) is False:
                raise ValueError('Dinner must be Meal')
            self.dinner = dinner

        if not lunch:
            self.lunch.update(p1=kwargs.pop('launch1', None), p2=kwargs.pop('launch2', None))

        if not dinner:
            self.dinner.update(p1=kwargs.pop('dinner1', None), p2=kwargs.pop('dinner2', None))

        if kwargs:
            raise ValueError(f'Invalid arguments: {kwargs}')
