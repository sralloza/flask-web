# EXCEPTIONS

class BaseMenusException(Exception):
    """Base menus exception."""


class MealError(BaseMenusException):
    """Meal error."""


class ParserError(BaseMenusException):
    """Parser error."""


# WARNINGS
class BaseMenusWarning(Warning):
    """Base menus warning."""


class MealWarning(BaseMenusWarning):
    """Meal warning."""
