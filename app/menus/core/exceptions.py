# EXCEPTIONS

class BaseMenusException(Exception):
    """Base menus exception."""


class MealError(BaseMenusException):
    """Meal error."""


# WARNINGS
class BaseMenusWarning(Warning):
    """Base menus warning."""


class MealWarning(BaseMenusWarning):
    """Meal warning."""
