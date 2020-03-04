"""This module contains the base classes related to
menus used in this application.
"""
import logging
import warnings
from datetime import date, datetime
from enum import Enum, unique
from typing import Union

from app.menus.models import DailyMenusDatabaseController
from app.utils import Translator, now
from app.menus.core.utils import PRINCIPAL_URL

from .exceptions import InvalidStateError, MealError, MealWarning

logger = logging.getLogger(__name__)


@unique
class LunchState(Enum):
    """States of meals."""

    LUNCH = "LUNCH"
    DINNER = "DINNER"
    NONE = "NONE"

    def __bool__(self):
        return self != LunchState.NONE


class Index:
    """Represents the interface to store temporal values of a DailyMenu."""

    def __init__(self, lunch=None, dinner=None, dt=None, state=None):
        """

        Notes:
            All args in this class are meant to be changed dinamically. They are not meant to be
            declared (it is only for testing purposes).

        Args:
            lunch (Meal): lunch of the DailyMenu
            dinner (Meal: dinner of the DailyMenu
            dt (date): date of the DailyMenu
            state (str): current state of the Index.

        """

        self._date = dt
        self._lunch = lunch or Meal()
        self._dinner = dinner or Meal()
        self._state = LunchState.NONE
        self.meal_combined = None

        if state:
            self.set_state(state)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return (
            f"Index(lunch={self.lunch!r}, dinner={self.dinner!r},"
            f" date={self.date}, state={self.state.value})"
        )

    @property
    def is_combinated(self):
        """Returns whether the meal is combinated or not.

        Returns:
            bool: True if the meal is combinated, False otherwise.
        """
        return self.meal_combined is not None

    def set_combined(self, meal_combined: Union[LunchState, str]):
        """Indicates that meal_combined is Combinated.

        Args:
            meal_combined: must be LUNCH or DINNER.

        """

        if not isinstance(meal_combined, LunchState):
            try:
                meal_combined = LunchState(meal_combined)
            except ValueError:
                raise MealError(f"Invalid meal: {meal_combined}")

        self.meal_combined = meal_combined

    @property
    def lunch(self):
        """Returns the lunch."""
        return self._lunch

    @property
    def dinner(self):
        """Returns the dinner."""
        return self._dinner

    @property
    def date(self):
        """Returns the date."""
        return self._date

    @property
    def state(self):
        """Returns the current state."""
        return self._state

    def commit(self):
        """Decides if the Index is ready to be stored in a database.
        The conditions are:
         - Have a date
         - Have a state
         - Have at least a non empty dinner or launch.
        """
        if not self.date:
            return False
        if not self.state:
            return False
        if not self.lunch.is_empty():
            return True
        if not self.dinner.is_empty():
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
            InvalidStateError: if an state is set.
        """

        if self.state == LunchState.LUNCH:
            return self.lunch.is_empty()
        if self.state == LunchState.DINNER:
            return self.dinner.is_empty()
        if not self.state:
            raise MealError("state not set while checking for emtpyness")
        return None

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

        warnings.warn(f"Could not decide: {text}", MealWarning, stacklevel=2)
        return False

    def set_state(self, state: Union[LunchState, str]):
        """Sets the actual state.

        Raises:
            InvalidStateError: if the state is invalid.
        """

        if not isinstance(state, LunchState):
            try:
                state = LunchState(state)
            except ValueError:
                raise InvalidStateError(f"Invalid state: {state}")

        self._state = state

    def set_first(self, first):
        """Sets the first plate.

        Raises:
            RuntimeError: if no state is set.
        """

        first = first.strip()

        if not first:
            return

        if not self.state:
            raise RuntimeError("State not set")

        if self.state == LunchState.LUNCH:
            self.lunch.p1 = first
        elif self.state == LunchState.DINNER:
            self.dinner.p1 = first

    def get_first(self):
        """Returns the first plate."""

        if self.state == LunchState.LUNCH:
            return self.lunch.p1
        if self.state == LunchState.DINNER:
            return self.dinner.p1
        return None

    def set_second(self, second):
        """Sets the second plate.

        Raises:
            RuntimeError: if no state is set.
        """

        second = second.strip()

        if not second:
            return

        if not self.state:
            raise RuntimeError("State not set")

        if self.state == LunchState.LUNCH:
            self.lunch.p2 = second
        elif self.state == LunchState.DINNER:
            self.dinner.p2 = second

    def get_second(self):
        """Gets the second plate.

        Raises:
            InvalidStateError: if the state is invalid.
        """

        if self.state == LunchState.LUNCH:
            return self.lunch.p2
        if self.state == LunchState.DINNER:
            return self.dinner.p2
        return None

    def to_dict(self):
        """Returns the lunch and dinner info as a dict."""
        return {"lunch": self.lunch, "dinner": self.dinner}


class Meal:
    """Represents a meal, which consists of two plates."""

    def __init__(self, p1=None, p2=None):
        self.p1 = p1
        self.p2 = p2

        self.strip()

    def __repr__(self):
        return f"{self.p1} - {self.p2}"

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def is_empty(self):
        """Checks that no plate is configured."""
        return self.p1 is None and self.p2 is None

    def update(self, **kwargs):
        """Updates plates.

        Keyword Args:
            p1 (str): first plate.
            p2 (str): second plate.

        """

        p1 = kwargs.pop("p1", None)
        p2 = kwargs.pop("p2", None)

        if p1:
            self.p1 = p1
        if p2:
            self.p2 = p2

        if kwargs:
            raise ValueError(f"Invalid arguments for Meal: {kwargs}")

        self.strip()

    def strip(self):
        """Strips plates."""
        if self.p1:
            self.p1 = self.p1.strip().lower()

        if self.p2:
            self.p2 = self.p2.strip().lower()


class Combined(Meal):
    """Meal which only has one plate."""

    def __init__(self, p1=None):
        super().__init__(p1=p1, p2=None)

        self.strip()

    def is_empty(self):
        """Checks if the combined is empty."""
        return self.p1 is None

    def update(self, **kwargs):
        """Updates plates.

        Keyword Args:
            p1 (str): fist and only plate.
        """

        self.p1 = self.p1 or kwargs.pop("p1", None)

        if kwargs:
            raise ValueError(f"Invalid arguments for Combined: {kwargs}")

        self.strip()


class DailyMenu:
    """Represents the menu of a day.

    Args:
        day (int): day of the menu.
        month (int): month of the menu.
        year (int): year of the menu.
        lunch (Meal, optional): lunch of the menu. Defaults to None.
        dinner (Meal, optional): dinner of the menu. Defaults to None.
        url (str, optional): url where the menu was parsed from. Defaults to None.
    """

    def __init__(self, day, month, year, lunch=None, dinner=None, url=None):
        self.day = day
        self.month = month
        self.year = year
        self.lunch = lunch or Meal()
        self.dinner = dinner or Meal()
        self.url = url or PRINCIPAL_URL

        self.date = date(self.year, self.month, self.day)
        self.weekday = Translator.english_to_spanish(self.date.strftime("%A").lower())
        self.id = int(f"{self.year:04d}{self.month:02d}{self.day:02d}")
        self.is_today = self.date == now().date()
        self.code = "dia" if self.is_today else ""

    def __eq__(self, other):
        if not isinstance(other, DailyMenu):
            raise TypeError(
                f"'==' must be used with DailyMenu, not {type(other).__name__!r} ({other!r})"
            )

        return (
            self.day == other.day
            and self.month == other.month
            and self.year == other.year
            and self.lunch == other.lunch
            and self.dinner == other.dinner
        )

    def __str__(self):
        return self.format_date()

    def __repr__(self):
        return f"%s(%s, lunch=%r, dinner=%r)" % (
            type(self).__name__,
            self.date,
            self.lunch,
            self.dinner,
        )

    def is_empty(self):
        """Checks if lunch and dinner are emtpy."""
        try:
            return self.lunch.is_empty() and self.dinner.is_empty()
        except AttributeError:
            return False

    def set_combined(self, meal: Union[LunchState, str]):
        """Sets the meal to combinated.

        Args:
            meal (LunchState or str): meal to set to combinated

        Raises:
            MealError: if `meal` is not a valid meal.
        """
        if not isinstance(meal, LunchState):
            try:
                meal = LunchState(meal)
            except ValueError:
                raise MealError(f"meal must be LunchState, not {type(meal).__name__}")

        if meal == LunchState.LUNCH:
            self.lunch.p1 = Combined()

        if meal == LunchState.DINNER:
            self.dinner.p1 = Combined()

    def to_database(self):
        """Saves the menu to the database."""
        # logger.debug('Saving menu %d to database', self.id)
        result = DailyMenusDatabaseController.save_daily_menu(self)
        if result is True:
            logger.info("Saved menu %d to database", self.id)
        return result

    def remove_from_database(self):
        """Removes the menu from the database."""
        result = DailyMenusDatabaseController.remove_daily_menu(self)
        if result is True:
            logger.info("removed menu %d from the database", self.id)
        return result

    def to_string(self):
        """Returns the menu formatted as a string."""

        string = ""
        string += f"{self.format_date()}\n"

        if not self.lunch.is_empty():
            string += f" - Comida\n"
            string += f"   - {self.lunch.p1}\n"

            if self.lunch.p2:
                string += f"   - {self.lunch.p2}\n"

        if not self.dinner.is_empty():
            string += f" - Cena\n"
            string += f"   - {self.dinner.p1}\n"

            if self.dinner.p2:
                string += f"   - {self.dinner.p2}\n"

        return string

    def to_html(self):
        """Returns the menu formatted as html."""
        return self.to_string().replace("\n", "<br>")

    @classmethod
    def from_datetime(cls, timestamp: Union[datetime, str, date]):
        """Creates a DailyMenu given its datetime.

        Args:
            timestamp (datetime, str or date): datetime of the menu.

        """

        self = DailyMenu.__new__(DailyMenu)

        if isinstance(timestamp, str):
            timestamp = timestamp.lower()
            timestamp = timestamp.replace("miercoles", "miércoles")
            timestamp = timestamp.replace("sabado", "sábado")
            timestamp = datetime.strptime(
                Translator.spanish_to_english(timestamp), "día: %d de %B de %Y (%A)"
            )

        if not isinstance(timestamp, (datetime, date)):
            raise TypeError(
                f"timestamp must be datetime or str, not {type(timestamp).__name__}"
            )

        self.__init__(timestamp.day, timestamp.month, timestamp.year, None, None, None)

        return self

    def format_date(self, long=True):
        """Returns the day formatted of the menu."""
        if not long:
            return str(self.date)
        return Translator.english_to_spanish(self.date.strftime("%d de %B de %Y (%A)"))

    def update(self, **kwargs):
        """Updates values of the menu.

        Keyword Args:
            lunch (Meal): whole lunch as Meal.
            dinner (Meal): whole dinner as Meal.
            lunch1 (str): first plate of lunch.
            lunch2 (str): second plate of lunch.
            dinner1 (str): first plate of dinner.
            dinner2 (str): second plate of dinner.

        """

        lunch = kwargs.pop("lunch", None)
        dinner = kwargs.pop("dinner", None)

        if lunch:
            if isinstance(lunch, Meal) is False:
                raise ValueError("Lunch must be Meal")
            self.lunch = lunch

        if dinner:
            if isinstance(dinner, Meal) is False:
                raise ValueError("Dinner must be Meal")
            self.dinner = dinner

        if not lunch:
            self.lunch.update(
                p1=kwargs.pop("lunch1", None), p2=kwargs.pop("lunch2", None)
            )

        if not dinner:
            self.dinner.update(
                p1=kwargs.pop("dinner1", None), p2=kwargs.pop("dinner2", None)
            )

        if kwargs:
            raise ValueError(f"Invalid arguments: {kwargs}")
