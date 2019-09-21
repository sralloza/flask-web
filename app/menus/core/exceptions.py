# EXCEPTIONS

class BaseMenusError(Exception):
    """Base menus exception."""


class MealError(BaseMenusError):
    """Meal error."""


class ParserError(BaseMenusError):
    """Parser error."""


# WARNINGS
class BaseMenusWarning(Warning):
    """Base menus warning."""


class MealWarning(BaseMenusWarning):
    """Meal warning."""
