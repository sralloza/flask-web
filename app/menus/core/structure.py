import logging
import re
import warnings
from datetime import datetime, date
from typing import Union

from sqlalchemy.exc import IntegrityError

from app.menus.models import DailyMenuDB, db
from .exceptions import MealError, MealWarning

logger = logging.getLogger(__name__)


class Index:
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
            state (str): current state of the Index. Its valid states are declared in
                Index._valid_states.
        """

        self._date = dt
        self._lunch = lunch or Meal()
        self._dinner = dinner or Meal()
        self._state = None
        self.is_combinated = False
        self.meal_combined = None

        if state:
            self.set_state(state)

    def __repr__(self):
        return f'Index(lunch={self.lunch!r}, dinner={self.dinner!r},' \
            f' date={self.date!r}, state={self.state!r})'

    def set_combined(self, meal_combined):
        if meal_combined not in ('LUNCH', 'DINNER'):
            raise MealError(f'Invalid meal: {meal_combined}')

        self.is_combinated = True
        self.meal_combined = meal_combined

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

    @property
    def state(self):
        return self._state

    def commit(self):
        """Decides if the Index is ready to be stored in a database.
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
        """Deletes all the temporal values of the Index."""
        self.__init__()

    def set_date(self, new_date: date):
        """Sets a new date."""
        self._date = new_date

    def is_current_meal_empty(self):
        """Detects if the actual meal is empty.

        Raises
            MealError: if no state is configured.
            MealError: if an invalid value is set for meal_type.
        """

        if self._state == 'LUNCH':
            return self._lunch.is_empty()
        elif self._state == 'DINNER':
            return self._dinner.is_empty()
        elif self._state is None:
            raise MealError('Meal_type is None while checking for emtpyness')
        raise MealError(f'Invalid value for meal_type: {self._state}')

    def decide(self, text: str):
        """Called if the normal algorithm couldn't idenfity content.

        If the current meal is emtpy, it will asssume content is the fist plate. Otherwise, a
        warning will be raised.

        Warnings:
            MealWarning: if the current meal is not empty, which means that the secondary
                algorithm couldn't make a decition.

        Raises:
            MealError: if no state is configured (via Index.is_current_meal_empty)

        Returns:
            bool: True if everything went right, false otherwise.

        """

        if self.is_current_meal_empty():
            self.set_first(text)
            return True
        else:
            warnings.warn(f'Could not decide: {text}', MealWarning, stacklevel=2)
            return False

    def set_state(self, meal_type):
        """Sets the actual state.

        Raises:
            ValueError: if the meal_type is invalid.
        """

        if meal_type not in self._valid_states:
            raise ValueError('Invalid meal type: %s from %r'.format(meal_type, self._valid_states))
        self._state = meal_type

    def set_first(self, first):
        """Sets the first plate.

        Raises:
            RuntimeError: if no state is set.
            ValueError: if the meal_type is invalid.
        """

        first = first.strip()

        if not first:
            return

        if not self._state:
            raise RuntimeError('Meal type not set')

        if self._state == 'LUNCH':
            self._lunch.p1 = first
        elif self.meal_type == 'DINNER':
            self._dinner.p1 = first
        else:
            raise ValueError(f'Invalid meal type: {self._state}')

    def get_first(self):
        """Returns the first plate.

        Raises:
            ValueError: if the meal_type is invalid.
        """

        if self._state == 'LUNCH':
            return self._lunch.p1
        elif self.meal_type == 'DINNER':
            return self._dinner.p1
        else:
            raise ValueError(f'Invalid meal type: {self._state}')

    def set_second(self, second):
        """Sets the second plate.

        Raises:
            RuntimeError: if no state is set.
            ValueError: if the meal_type is invalid.
        """

        second = second.strip()

        if not second:
            return

        if not self._state:
            raise RuntimeError('Meal type not set')

        if self._state == 'LUNCH':
            self._lunch.p2 = second
        elif self._state == 'DINNER':
            self._dinner.p2 = second
        else:
            raise ValueError(f'Invalid meal type: {self._state}')

    def get_second(self):
        """Gets the second plate.

        Raises:
            ValueError: if the meal_type is invalid.
        """

        if self._state == 'LUNCH':
            return self._lunch.p2
        elif self._state == 'DINNER':
            return self._dinner.p2
        else:
            raise ValueError(f'Invalid meal type: {self._state}')

    def to_dict(self):
        """Returns the lunch and dinner info as a dict."""
        return {'lunch': self._lunch, 'dinner': self._dinner}


class Meal:
    def __init__(self, p1=None, p2=None):
        self.p1 = p1
        self.p2 = p2

        self.strip()

    def __repr__(self):
        return f'{self.p1} - {self.p2}'

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def is_empty(self):
        return self.p1 is None and self.p2 is None

    def update(self, **kwargs):
        p1 = kwargs.pop('p1', None)
        p2 = kwargs.pop('p2', None)

        if p1:
            self.p1 = p1
        if p2:
            self.p2 = p2

        if kwargs:
            raise ValueError(f'Invalid arguments for Meal: {kwargs}')

        self.strip()

    def strip(self):
        if self.p1:
            self.p1 = self.p1.strip()

        if self.p2:
            self.p2 = self.p2.strip()


class Combined(Meal):
    def __init__(self, p1=None):
        super().__init__(p1=p1)
        self.p1 = p1
        self.p2 = None

        self.strip()

    def is_empty(self):
        return self.p1 is None

    def update(self, **kwargs):
        self.p1 = self.p1 or kwargs.pop('p1', None)

        if kwargs:
            raise ValueError(f'Invalid arguments for Combined: {kwargs}')

        self.strip()


class DailyMenu:
    """Represents the menu of a day."""

    _e_to_s_weekdays = {'monday': 'lunes', 'tuesday': 'martes', 'wednesday': 'miércoles',
                        'thursday': 'jueves', 'friday': 'viernes', 'saturday': 'sábado',
                        'sunday': 'domingo'}
    _s_to_e_weekdays = {'lunes': 'monday', 'martes': 'tuesday', 'miércoles': 'wednesday',
                        'jueves': 'thursday', 'viernes': 'friday', 'sábado': 'saturday',
                        'domingo': 'sunday'}

    _e_to_s_months = {'january': 'enero', 'february': 'febrero', 'march': 'marzo', 'april': 'abril',
                      'may': 'mayo', 'june': 'junio', 'july': 'julio', 'august': 'agosto',
                      'september': 'septiembre', 'october': 'octubre', 'november': 'noviembre',
                      'december': 'diciembre'}
    _s_to_e_months = {'enero': 'january', 'febrero': 'february', 'marzo': 'march', 'abril': 'april',
                      'mayo': 'may', 'junio': 'june', 'julio': 'july', 'agosto': 'august',
                      'septiembre': 'september', 'octubre': 'october', 'noviembre': 'november',
                      'diciembre': 'december'}

    def __init__(self, day: int, month: int, year: int, lunch: Meal = None, dinner: Meal = None):
        self.day = day
        self.month = month
        self.year = year
        self.lunch = lunch or Meal()
        self.dinner = dinner or Meal()

        self.date = date(self.year, self.month, self.day)
        self.weekday = self._e_to_s_weekdays[self.date.strftime('%A').lower()]
        self.id = int(f'{self.year:04d}{self.month:02d}{self.day:02d}')
        self.is_today = self.date == datetime.today().date()
        self.code = 'dia' if self.is_today else ''

    def __eq__(self, other):
        if not isinstance(other, DailyMenu):
            raise TypeError(
                f"'==' must be used with DailyMenu, not {type(other).__name__!r} ({other!r})")

        return (self.day == other.day and self.month == other.month and self.year == other.year
                and self.lunch == other.lunch and self.dinner == other.dinner)

    def __str__(self):
        return self.format_date()

    def __repr__(self):
        return str(self)

    def is_empty(self):
        try:
            return self.lunch.is_empty() and self.dinner.is_empty()
        except AttributeError:
            return False

    def set_combined(self, meal: str):
        if meal not in ('LUNCH', 'DINNER'):
            raise ValueError(f'meal must be LUNCH or DINNER, not {meal}')

        if meal == 'LUNCH':
            self.lunch.p1 = Combined()

        if meal == 'DINNER':
            self.dinner.p1 = Combined()

    def to_database(self):
        """Saves the menu to the database."""
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
            db.session.rollback()
            return False
        finally:
            db.session.close()

    def to_string(self):
        """Returns the menu formatted as a string."""

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
        """Returns the menu formatted as html."""
        return self.to_string().replace('\n', '<br>')

    @staticmethod
    def e_to_s(text):
        """Converts months and weekdays from english to spanish."""
        text = text.lower()
        for key, value in DailyMenu._e_to_s_months.items():
            text = re.sub(key, value, text, re.I)

        for key, value in DailyMenu._e_to_s_weekdays.items():
            text = text.replace(key, value)

        return text

    @staticmethod
    def s_to_e(text):
        """Converts months and weekdays from spanish to english."""
        text = text.lower()
        for key, value in DailyMenu._s_to_e_months.items():
            text = re.sub(key, value, text, re.I)

        for key, value in DailyMenu._s_to_e_weekdays.items():
            text = text.replace(key, value)

        return text

    @classmethod
    def from_datetime(cls, dt: Union[datetime, str, date]):
        """Creates a DailyMenu given its datetime.

        Args:
            dt (datetime, str, date): datetime of the menu.
        """

        self = DailyMenu.__new__(DailyMenu)

        if isinstance(dt, str):
            dt = dt.lower()
            dt = dt.replace('miercoles', 'miércoles')
            dt = dt.replace('sabado', 'sábado')
            dt = datetime.strptime(self.s_to_e(dt), 'día: %d de %B de %Y (%A)')

        if not isinstance(dt, (datetime, date)):
            raise TypeError(f'dt must be datetime or str, not {type(dt).__name__}')

        self.__init__(dt.day, dt.month, dt.year)

        return self

    def format_date(self, long=True):
        """Returns the day formatted of the menu."""
        if not long:
            return str(self.date)
        return self.e_to_s(self.date.strftime('%d de %B de %Y (%A)'))

    def update(self, **kwargs):
        """Updates values of the menu."""
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
            self.lunch.update(p1=kwargs.pop('lunch1', None), p2=kwargs.pop('lunch2', None))

        if not dinner:
            self.dinner.update(p1=kwargs.pop('dinner1', None), p2=kwargs.pop('dinner2', None))

        if kwargs:
            raise ValueError(f'Invalid arguments: {kwargs}')
