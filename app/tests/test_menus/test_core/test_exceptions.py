import warnings

import pytest

from app.menus.core.exceptions import BaseMenusException, MealError, BaseMenusWarning, MealWarning


def test_base_menus_exception():
    with pytest.raises(BaseMenusException):
        raise BaseMenusException

    assert issubclass(BaseMenusException, Exception)


def test_meal_error():
    with pytest.raises(MealError):
        raise MealError

    assert issubclass(MealError, BaseMenusException)


def test_base_menus_warning():
    with pytest.warns(BaseMenusWarning):
        warnings.warn('Dummy', BaseMenusWarning)

    assert issubclass(BaseMenusWarning, Warning)


def test_meal_warning():
    with pytest.warns(MealWarning):
        warnings.warn('Dummy', MealWarning)

    assert issubclass(MealWarning, BaseMenusWarning)
