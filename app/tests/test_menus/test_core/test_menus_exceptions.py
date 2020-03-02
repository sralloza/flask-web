import warnings

import pytest

from app.menus.core.exceptions import (
    BaseMenusError,
    BaseMenusWarning,
    InvalidStateError,
    MealError,
    MealWarning,
)


def test_base_menus_exception():
    with pytest.raises(BaseMenusError):
        raise BaseMenusError

    assert issubclass(BaseMenusError, Exception)


def test_meal_error():
    with pytest.raises(MealError):
        raise MealError

    assert issubclass(MealError, BaseMenusError)


def test_invalid_state_error():
    with pytest.raises(InvalidStateError):
        raise InvalidStateError

    assert issubclass(InvalidStateError, BaseMenusError)


def test_base_menus_warning():
    with pytest.warns(BaseMenusWarning):
        warnings.warn("Dummy", BaseMenusWarning)

    assert issubclass(BaseMenusWarning, Warning)


def test_meal_warning():
    with pytest.warns(MealWarning):
        warnings.warn("Dummy", MealWarning)

    assert issubclass(MealWarning, BaseMenusWarning)
