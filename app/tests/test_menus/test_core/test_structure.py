import datetime
import itertools
from unittest import mock

import pytest

from app.menus.core.exceptions import InvalidStateError, MealError, MealWarning
from app.menus.core.structure import Combined, DailyMenu
from app.menus.core.structure import Index
from app.menus.core.structure import LunchState, Meal

# Test data
mydate = (datetime.date(2019, 1, 1), None)
lunch = (Meal("lunch1", "lunch2"), None)
dinner = (Meal("dinner1", "dinner2"), None)
states = ("LUNCH", "DINNER", None)


def gen_indexes():
    _params = list(itertools.product(lunch, dinner, mydate, states))
    return [Index(*a) for a in _params]


class TestIndex:
    _commit = [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    _emtpy = [0, 0, 2, 0, 0, 2, 0, 1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 2, 1, 1, 2, 1, 1, 2]
    _decide = [0, 0, 2, 0, 0, 2, 0, 1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 2, 1, 1, 2, 1, 1, 2]
    _dicts = [3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]

    def test_repr(self):
        index = Index(
            Meal("a", "b"), Meal("c", "d"), datetime.date(2000, 1, 1), "LUNCH"
        )
        repr_expected = (
            "Index(lunch=a - b, dinner=c - d, " "date=2000-01-01, state=LUNCH)"
        )
        assert repr(index) == repr_expected

    def test_str(self):
        index = Index(
            Meal("a", "b"), Meal("c", "d"), datetime.date(2000, 1, 1), "LUNCH"
        )
        str_expected = (
            "Index(lunch=a - b, dinner=c - d, " "date=2000-01-01, state=LUNCH)"
        )
        assert str(index) == str_expected

    @pytest.mark.parametrize("index, commit", list(zip(gen_indexes(), _commit)))
    def test_commit(self, index, commit):
        assert index.commit() == bool(commit)

    @pytest.mark.parametrize("index, empty", list(zip(gen_indexes(), _emtpy)))
    def test_is_actual_meal_empty(self, index, empty):
        if empty == 2:
            with pytest.raises(
                MealError, match="state not set while checking for emtpyness"
            ):
                index.is_current_meal_empty()
        else:
            assert index.is_current_meal_empty() == bool(empty)

    @pytest.mark.parametrize("index, decide", list(zip(gen_indexes(), _decide)))
    def test_decide(self, index, decide):
        if decide == 2:
            with pytest.raises(
                MealError, match="state not set while checking for emtpyness"
            ):
                assert index.is_current_meal_empty()
        elif decide == 1:
            assert index.decide("hello-world")
            assert index.get_first() == "hello-world"
        else:
            with pytest.warns(MealWarning, match="Could not decide: hello-world"):
                assert not index.decide("hello-world")

    def test_set_state(self):
        i = Index()
        i.set_state("LUNCH")
        assert i.state == LunchState.LUNCH

        i.set_state("DINNER")
        assert i.state == LunchState.DINNER

        with pytest.raises(InvalidStateError, match="Invalid state"):
            i.set_state("DUMMY")

        with pytest.raises(InvalidStateError, match="Invalid state"):
            i.set_state("LAUNCH")

    def test_set_first(self):
        i = Index()

        with pytest.raises(RuntimeError, match="State not set"):
            i.set_first("dummy")

        i.set_state("LUNCH")
        i.set_first("test first lunch")
        assert i.lunch.p1 == "test first lunch"

        i.set_state("DINNER")
        i.set_first("test first dinner")
        assert i.dinner.p1 == "test first dinner"

        i.set_first("")
        assert i.dinner.p1 == "test first dinner"

    def test_get_first(self):
        i = Index()

        i.set_state("LUNCH")
        i.set_first("test first lunch")
        assert i.get_first() == "test first lunch"

        i.set_state("DINNER")
        i.set_first("test first dinner")
        assert i.get_first() == "test first dinner"

        i.set_first("")
        assert i.get_first() == "test first dinner"

    def test_set_second(self):
        i = Index()

        with pytest.raises(RuntimeError, match="State not set"):
            i.set_second("dummy")

        i.set_state("LUNCH")
        i.set_second("test second lunch")
        assert i.lunch.p2 == "test second lunch"

        i.set_state("DINNER")
        i.set_second("test second dinner")
        assert i.dinner.p2 == "test second dinner"

        i.set_second("")
        assert i.dinner.p2 == "test second dinner"

    def test_get_second(self):
        i = Index()

        i.set_state("LUNCH")
        i.set_second("test first lunch")
        assert i.get_second() == "test first lunch"

        i.set_state("DINNER")
        i.set_second("test first dinner")
        assert i.get_second() == "test first dinner"

        i.set_second("")
        assert i.get_second() == "test first dinner"

    def test_set_combined_str(self):
        i = Index()
        assert not i.is_combinated
        assert i.meal_combined is None

        i.set_combined("LUNCH")
        assert i.is_combinated
        assert i.meal_combined == LunchState.LUNCH

        i.set_combined("DINNER")
        assert i.is_combinated
        assert i.meal_combined == LunchState.DINNER

    def test_set_combined_enum(self):
        i = Index()
        assert not i.is_combinated
        assert i.meal_combined is None

        i.set_combined(LunchState.LUNCH)
        assert i.is_combinated
        assert i.meal_combined == LunchState.LUNCH

        i.set_combined(LunchState.DINNER)
        assert i.is_combinated
        assert i.meal_combined == LunchState.DINNER

    def test_set_combined_error(self):
        i = Index()
        with pytest.raises(MealError, match="Invalid meal"):
            i.set_combined("dummy")

    @pytest.mark.parametrize("index, dictcode", list(zip(gen_indexes(), _dicts)))
    def test_to_dict(self, index, dictcode):
        # 0 -> none, 1 -> dinner, 2 -> lunch, 3 -> both

        if dictcode == 0:
            assert index.to_dict() == {"lunch": Meal(), "dinner": Meal()}
        elif dictcode == 1:
            assert index.to_dict() == {"lunch": Meal(), "dinner": dinner[0]}
        elif dictcode == 2:
            assert index.to_dict() == {"lunch": lunch[0], "dinner": Meal()}
        elif dictcode == 3:
            assert index.to_dict() == {"lunch": lunch[0], "dinner": dinner[0]}


def gen_meals():
    p1 = ("meal_1", None)
    p2 = ("meal_2", None)

    _params = list(itertools.product(p1, p2))
    return [Meal(*a) for a in _params]


class TestMeal:
    _is_empty = [0, 0, 0, 1]

    @pytest.mark.parametrize("meal, is_empty", list(zip(gen_meals(), _is_empty)))
    def test_is_empty(self, meal, is_empty):
        if is_empty == 1:
            assert meal.is_empty()
        else:
            assert not meal.is_empty()

    def test_update(self):
        m1 = Meal()
        m2 = Meal()
        m3 = Meal()
        m4 = Meal()

        m1.update(p1=None, p2=None)

        assert m1.p1 is None
        assert m1.p2 is None

        m2.update(p1="meal_1", p2=None)
        assert m2.p1 == "meal_1"
        assert m2.p2 is None

        m3.update(p1=None, p2="meal_2")
        assert m3.p1 is None
        assert m3.p2 == "meal_2"

        m4.update(p1="meal_1", p2="meal_2")
        assert m4.p1 == "meal_1"
        assert m4.p2 == "meal_2"

        with pytest.raises(
            ValueError, match="Invalid arguments for Meal: {'foo': 'bar'}"
        ):
            m1.update(foo="bar", p1="new_meal")

        assert m1.p1 == "new_meal"

    def test_force_update(self):
        meal = Meal()
        meal.update(p1="p1", p2="p2")
        assert meal.p1 == "p1"
        assert meal.p2 == "p2"

        meal.update(p1="new-1", p2="new-2")
        assert meal.p1 == "new-1"
        assert meal.p2 == "new-2"

    def test_strip(self):
        m = Meal(p1=" mEaL-1 ", p2="   MeaL-2   ")
        m.strip()

        assert m.p1 == "meal-1"
        assert m.p2 == "meal-2"


class TestCombined:
    def test_attributes(self):
        combined = Combined("hello")
        assert combined.p1 == "hello"
        assert combined.p2 is None

    def test_is_empty(self):
        combined_1 = Combined("hello")
        combined_2 = Combined()
        assert not combined_1.is_empty()
        assert combined_2.is_empty()

    def test_update(self):
        combined = Combined()
        combined.update(p1="hello")
        assert combined.p1 == "hello"

        with pytest.raises(ValueError, match="Invalid arguments for Combined"):
            combined.update(p2="world")


def gen_daily_menus():
    lunch = (Meal(), Meal(p1="lunch-1"), Meal(p1="lunch-1", p2="lunch-2"))
    dinner = (Meal(), Meal(p1="dinner-1"), Meal(p1="dinner-1", p2="dinner-2"))

    product = list(itertools.product(lunch, dinner))
    dates = [(x, 1, 2019) for x in range(1, len(product) + 1)]
    return [DailyMenu(*x, *k) for x, k in zip(dates, product)]


class TestDailyMenu:
    datetimes = (
        ("Día: 13 de diciembre de 2016 (martes)", datetime.date(2016, 12, 13)),
        ("Día: 13 de enero de 2017 (viernes)", datetime.date(2017, 1, 13)),
        ("Día: 23 de febrero de 2017 (jueves)", datetime.date(2017, 2, 23)),
        ("Día: 6 de marzo de 2017 (lunes)", datetime.date(2017, 3, 6)),
        ("Día: 9 de abril de 2017 (domingo)", datetime.date(2017, 4, 9)),
        ("Día: 30 de mayo de 2017 (martes)", datetime.date(2017, 5, 30)),
        ("Día: 28 de junio de 2017 (miércoles)", datetime.date(2017, 6, 28)),
        ("Día: 14 de julio de 2017 (viernes)", datetime.date(2017, 7, 14)),
        ("Día: 15 de agosto de 2017 (martes)", datetime.date(2017, 8, 15)),
        ("Día: 22 de septiembre de 2017 (viernes)", datetime.date(2017, 9, 22)),
        ("Día: 16 de octubre de 2017 (lunes)", datetime.date(2017, 10, 16)),
        ("Día: 7 de noviembre de 2017 (martes)", datetime.date(2017, 11, 7)),
        ("Día: 13 de diciembre de 2017 (miércoles)", datetime.date(2017, 12, 13)),
        (datetime.date(2016, 12, 13), datetime.date(2016, 12, 13)),
        (datetime.date(2017, 1, 13), datetime.date(2017, 1, 13)),
        (datetime.date(2017, 2, 23), datetime.date(2017, 2, 23)),
        (datetime.date(2017, 3, 6), datetime.date(2017, 3, 6)),
        (datetime.date(2017, 4, 9), datetime.date(2017, 4, 9)),
        (datetime.date(2017, 5, 30), datetime.date(2017, 5, 30)),
        (datetime.date(2017, 6, 28), datetime.date(2017, 6, 28)),
        (datetime.date(2017, 7, 14), datetime.date(2017, 7, 14)),
        (datetime.date(2017, 8, 15), datetime.date(2017, 8, 15)),
        (datetime.date(2017, 9, 22), datetime.date(2017, 9, 22)),
        (datetime.date(2017, 10, 16), datetime.date(2017, 10, 16)),
        (datetime.date(2017, 11, 7), datetime.date(2017, 11, 7)),
        (datetime.date(2017, 12, 13), datetime.date(2017, 12, 13)),
    )

    format_dates = (
        (datetime.date(2016, 12, 13), "13 de diciembre de 2016 (martes)"),
        (datetime.date(2017, 1, 13), "13 de enero de 2017 (viernes)"),
        (datetime.date(2017, 2, 23), "23 de febrero de 2017 (jueves)"),
        (datetime.date(2017, 3, 6), "06 de marzo de 2017 (lunes)"),
        (datetime.date(2017, 4, 9), "09 de abril de 2017 (domingo)"),
        (datetime.date(2017, 5, 30), "30 de mayo de 2017 (martes)"),
        (datetime.date(2017, 6, 28), "28 de junio de 2017 (miércoles)"),
        (datetime.date(2017, 7, 14), "14 de julio de 2017 (viernes)"),
        (datetime.date(2017, 8, 15), "15 de agosto de 2017 (martes)"),
        (datetime.date(2017, 9, 22), "22 de septiembre de 2017 (viernes)"),
        (datetime.date(2017, 10, 16), "16 de octubre de 2017 (lunes)"),
        (datetime.date(2017, 11, 7), "07 de noviembre de 2017 (martes)"),
        (datetime.date(2017, 12, 13), "13 de diciembre de 2017 (miércoles)"),
    )

    _to_str = (
        "1-martes-0-0",
        "2-miércoles-0-1",
        "3-jueves-0-2",
        "4-viernes-1-0",
        "5-sábado-1-1",
        "6-domingo-1-2",
        "7-lunes-2-0",
        "8-martes-2-1",
        "9-miércoles-2-2",
    )

    def test_equal(self):
        menu1 = DailyMenu(1, 1, 2000, Meal("a", "b"), Meal("c", "d"))
        menu2 = DailyMenu(1, 1, 2000, Meal("a", "b"), Meal("c", "d"))

        assert menu1 == menu2

        with pytest.raises(TypeError):
            menu1 == object()

    def test_str(self):
        menu = DailyMenu(1, 1, 2000, Meal("a", "b"), Meal("c", "d"))
        assert str(menu) == menu.format_date()

    def test_repr(self):
        menu = DailyMenu(1, 2, 2000, Meal("a", "b"), Meal("c", "d"))
        assert repr(menu) == "DailyMenu(2000-02-01, lunch=a - b, dinner=c - d)"

    @pytest.mark.parametrize("dm, str_code", list(zip(gen_daily_menus(), _to_str)))
    def test_to_string(self, dm, str_code):
        # Code: day-weekday-lunch_code-dinner_code
        # Meals codes: 0 -> emtpy, 1 -> P1, 2 -> P1 & P2

        day, weekday, lunch_code, dinner_code = str_code.split("-")

        day = int(day)
        day_str = f"{day:02d} de enero de 2019 ({weekday})\n"

        lunch_code = int(lunch_code)
        lunch_str = ""
        if lunch_code != 0:
            lunch_str += " - Comida\n"
            lunch_str += "   - lunch-1\n"
        if lunch_code == 2:
            lunch_str += "   - lunch-2\n"

        dinner_code = int(dinner_code)
        dinner_str = ""
        if dinner_code != 0:
            dinner_str += " - Cena\n"
            dinner_str += "   - dinner-1\n"
        if dinner_code == 2:
            dinner_str += "   - dinner-2\n"

        total_str = day_str + lunch_str + dinner_str

        assert dm.to_string() == total_str

    @pytest.mark.parametrize("dm, str_code", list(zip(gen_daily_menus(), _to_str)))
    def test_to_html(self, dm, str_code):
        # Code: day-weekday-lunch_code-dinner_code
        # Meals codes: 0 -> emtpy, 1 -> P1, 2 -> P1 & P2

        day, weekday, lunch_code, dinner_code = str_code.split("-")

        day = int(day)
        day_str = f"{day:02d} de enero de 2019 ({weekday})<br>"

        lunch_code = int(lunch_code)
        lunch_str = ""
        if lunch_code != 0:
            lunch_str += " - Comida<br>"
            lunch_str += "   - lunch-1<br>"
        if lunch_code == 2:
            lunch_str += "   - lunch-2<br>"

        dinner_code = int(dinner_code)
        dinner_str = ""
        if dinner_code != 0:
            dinner_str += " - Cena<br>"
            dinner_str += "   - dinner-1<br>"
        if dinner_code == 2:
            dinner_str += "   - dinner-2<br>"

        total_str = day_str + lunch_str + dinner_str

        assert dm.to_html() == total_str

    @pytest.mark.parametrize("dt_to_parse, dt_expected", datetimes)
    def test_from_datetime(self, dt_to_parse, dt_expected):
        assert DailyMenu.from_datetime(dt_to_parse).date == dt_expected

    def test_from_datetime_invalid(self):
        with pytest.raises(TypeError):
            DailyMenu.from_datetime(list())
        with pytest.raises(TypeError):
            DailyMenu.from_datetime(5654)
        with pytest.raises(TypeError):
            DailyMenu.from_datetime(15.65)
        with pytest.raises(TypeError):
            DailyMenu.from_datetime(1 + 9j)

    @pytest.mark.parametrize("dt_to_parse, str_expected", format_dates)
    def test_format_date_long(self, dt_to_parse, str_expected):
        assert DailyMenu.from_datetime(dt_to_parse).format_date() == str_expected

    sort_dates = tuple([x[0] for x in format_dates])

    @pytest.mark.parametrize("dt_to_parse", sort_dates)
    def test_format_date_short(self, dt_to_parse):
        assert DailyMenu.from_datetime(dt_to_parse).format_date(long=False) == str(
            dt_to_parse
        )

    def test_update(self):
        dm = DailyMenu(1, 1, 2019)

        lunch = Meal("lunch-1", "lunch-2")
        dinner = Meal("dinner-1", "dinner-2")

        dm.update(lunch=lunch, dinner=dinner)

        assert dm.lunch == lunch
        assert dm.dinner == dinner

        with pytest.raises(ValueError, match="Lunch must be Meal"):
            dm.update(lunch="peter")

        with pytest.raises(ValueError, match="Dinner must be Meal"):
            dm.update(dinner="pan")

        dm.update(
            lunch1="lunch1", lunch2="lunch2", dinner1="dinner1", dinner2="dinner2"
        )
        assert dm.lunch == Meal("lunch1", "lunch2")
        assert dm.dinner == Meal("dinner1", "dinner2")

    def test_update_extra_args(self):
        dm = DailyMenu(1, 1, 2019)

        with pytest.raises(ValueError):
            dm.update(foo="bar")

    data = (
        (DailyMenu(1, 1, 2000, Meal("a", "b"), Meal("c", "d")), False),
        (DailyMenu(1, 1, 2000, Meal("a", "b"), Meal("c")), False),
        (DailyMenu(1, 1, 2000, Meal("a", "b"), Meal()), False),
        (DailyMenu(1, 1, 2000, Meal("a"), Meal("c", "d")), False),
        (DailyMenu(1, 1, 2000, Meal("a"), Meal("c")), False),
        (DailyMenu(1, 1, 2000, Meal("a"), Meal()), False),
        (DailyMenu(1, 1, 2000, Meal(), Meal("c", "d")), False),
        (DailyMenu(1, 1, 2000, Meal(), Meal("c")), False),
        (DailyMenu(1, 1, 2000, Meal(), Meal()), True),
    )

    @pytest.mark.parametrize("daily_menu, should_be_emtpy", data)
    def test_is_empty_good(self, daily_menu, should_be_emtpy):
        assert daily_menu.is_empty() == should_be_emtpy

    def test_is_empty_fatal(self):
        menu1 = DailyMenu(31, 12, 1999, lunch=object())
        menu2 = DailyMenu(31, 12, 1999, dinner=object())

        assert menu1.is_empty() is False
        assert menu2.is_empty() is False

    def test_set_combined_str(self):
        dm = DailyMenu(1, 1, 2000)
        assert isinstance(dm.lunch, Meal)
        assert isinstance(dm.dinner, Meal)

        dm.set_combined("LUNCH")
        assert isinstance(dm.lunch, Meal)

        dm.set_combined("DINNER")
        assert isinstance(dm.dinner, Meal)

    def test_set_combined_enum(self):
        dm = DailyMenu(1, 1, 2000)
        assert isinstance(dm.lunch, Meal)
        assert isinstance(dm.dinner, Meal)

        dm.set_combined(LunchState.LUNCH)
        assert isinstance(dm.lunch, Meal)

        dm.set_combined(LunchState.DINNER)
        assert isinstance(dm.dinner, Meal)

    def test_set_combined_error(self):
        dm = DailyMenu(1, 1, 2000)
        with pytest.raises(MealError, match="meal must be LunchState"):
            dm.set_combined("dummy")

    @mock.patch("app.menus.core.structure.logger.info", autospec=True)
    def test_to_database(self, info_mock, client):
        menu = DailyMenu(31, 12, 2030)
        result = menu.to_database()

        info_mock.assert_called_once_with("Saved menu %d to database", 20301231)
        assert result is True

    @mock.patch("app.menus.core.structure.logger.info", autospec=True)
    def test_to_database_error(self, info_mock, client):
        menu = DailyMenu(31, 12, 2031)
        result_1 = menu.to_database()
        result_2 = menu.to_database()

        assert result_1 is True
        assert result_2 is False
        info_mock.assert_called_once_with("Saved menu %d to database", 20311231)

    @mock.patch("app.menus.core.structure.logger.info", autospec=True)
    def test_remove_from_database(self, info_mock, client):
        menu = DailyMenu(5, 12, 2025)
        result_1 = menu.remove_from_database()

        menu.to_database()
        result_2 = menu.remove_from_database()

        assert result_1 is False
        assert result_2 is True
