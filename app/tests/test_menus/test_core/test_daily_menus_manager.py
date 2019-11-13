import random
from datetime import date
from unittest import mock

import pytest

from app.menus.core.daily_menus_manager import DailyMenusManager
from app.menus.core.parser import Parsers
from app.menus.core.structure import DailyMenu, Meal
from app.menus.models import UpdateControl
from app.utils import now


@pytest.fixture
def dmm():
    dmm = DailyMenusManager()
    lunch = Meal("lunch-1", "lunch-2")
    dinner = Meal("dinner-1", "dinner-2")
    for e in range(1, 13):
        menu = DailyMenu(e, e, 2019, lunch, dinner)
        dmm.menus.append(menu)

    return dmm


# noinspection PyTypeChecker
def test_contains(dmm):
    assert date(2019, 1, 1) in dmm
    assert date(2019, 2, 2) in dmm
    assert date(2019, 3, 3) in dmm
    assert date(2019, 4, 4) in dmm
    assert date(2019, 5, 5) in dmm
    assert date(2019, 6, 6) in dmm
    assert date(2019, 7, 7) in dmm
    assert date(2019, 8, 8) in dmm
    assert date(2019, 9, 9) in dmm
    assert date(2019, 10, 10) in dmm
    assert date(2019, 11, 11) in dmm
    assert date(2019, 12, 12) in dmm

    with pytest.raises(TypeError, match="Contains does only work with dates"):
        assert object in dmm
    with pytest.raises(TypeError, match="Contains does only work with dates"):
        assert 5 in dmm
    with pytest.raises(TypeError, match="Contains does only work with dates"):
        assert 7 + 1j in dmm
    with pytest.raises(TypeError, match="Contains does only work with dates"):
        assert "error" in dmm


def test_getitem(dmm):
    assert dmm[date(2019, 1, 1)]
    assert dmm[date(2019, 2, 2)]
    assert dmm[date(2019, 3, 3)]
    assert dmm[date(2019, 4, 4)]
    assert dmm[date(2019, 5, 5)]
    assert dmm[date(2019, 6, 6)]

    with pytest.raises(TypeError, match="Getitem does only work with dates"):
        assert dmm[object]
    with pytest.raises(TypeError, match="Getitem does only work with dates"):
        assert dmm[5]
    with pytest.raises(TypeError, match="Getitem does only work with dates"):
        assert dmm[7 + 1j]
    with pytest.raises(TypeError, match="Getitem does only work with dates"):
        assert dmm["error"]

    with pytest.raises(KeyError, match="No menu found"):
        assert dmm[date(1970, 1, 1)]


def test_sort(dmm):
    random.shuffle(dmm.menus)

    ideal_dates = [x.date for x in dmm]
    ideal_dates.sort(reverse=True)
    dmm.sort()
    real_dates = [x.date for x in dmm]

    assert real_dates == ideal_dates


def test_to_string(dmm):
    string1 = dmm.to_string()
    string2 = str(dmm)
    string3 = repr(dmm)

    assert string1 == string2 == string3

    assert len(string1)
    assert string1.count("\n") == 95
    assert string1.count("(") == 12
    assert string1.count(")") == 12
    assert string1.count("(") == string1.count(")")

    assert string1.count("Comida") == 12
    assert string1.count("lunch-1") == 12
    assert string1.count("lunch-2") == 12
    assert string1.count("Comida") == string1.count("lunch-1")

    assert string1.count("Cena") == 12
    assert string1.count("dinner-1") == 12
    assert string1.count("dinner-2") == 12
    assert string1.count("Cena") == string1.count("dinner-1")


def test_to_html(dmm):
    string = dmm.to_html()

    assert len(string)
    assert string.count("<br>") == 95
    assert string.count("(") == 12
    assert string.count(")") == 12
    assert string.count("(") == string.count(")")

    assert string.count("Comida") == 12
    assert string.count("lunch-1") == 12
    assert string.count("lunch-2") == 12
    assert string.count("Comida") == string.count("lunch-1")

    assert string.count("Cena") == 12
    assert string.count("dinner-1") == 12
    assert string.count("dinner-2") == 12
    assert string.count("Cena") == string.count("dinner-1")


class TestAddToMenus:
    def test_one_menu(self):
        dmm = DailyMenusManager()

        menu = DailyMenu(
            6, 12, 2019, Meal("lunch1", "lunch2"), Meal("dinner-1", "dinner-2")
        )
        assert date(2019, 12, 6) not in dmm

        dmm.add_to_menus(menu)
        assert date(2019, 12, 6) in dmm

    def test_multiples_menus(self):
        dmm = DailyMenusManager()

        menu1 = DailyMenu(
            6, 12, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )
        menu2 = DailyMenu(
            6, 11, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )
        menu3 = DailyMenu(
            6, 10, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )

        assert date(2019, 12, 6) not in dmm
        assert date(2019, 11, 6) not in dmm
        assert date(2019, 10, 6) not in dmm

        dmm.add_to_menus([menu1, menu2, menu3])
        assert date(2019, 12, 6) in dmm
        assert date(2019, 11, 6) in dmm
        assert date(2019, 10, 6) in dmm

    def test_multiple_calls(self):
        dmm = DailyMenusManager()

        menu1 = DailyMenu(
            6, 12, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )
        menu2 = DailyMenu(
            6, 11, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )
        menu3 = DailyMenu(
            6, 10, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )

        assert len(dmm) == 0
        assert date(2019, 12, 6) not in dmm
        assert date(2019, 11, 6) not in dmm
        assert date(2019, 10, 6) not in dmm

        dmm.add_to_menus(menu1)
        assert len(dmm) == 1
        assert date(2019, 12, 6) in dmm
        assert date(2019, 11, 6) not in dmm
        assert date(2019, 10, 6) not in dmm

        dmm.add_to_menus(menu2)
        assert len(dmm) == 2
        assert date(2019, 12, 6) in dmm
        assert date(2019, 11, 6) in dmm
        assert date(2019, 10, 6) not in dmm

        dmm.add_to_menus(menu3)
        assert len(dmm) == 3
        assert date(2019, 12, 6) in dmm
        assert date(2019, 11, 6) in dmm
        assert date(2019, 10, 6) in dmm

    def test_add_duplicate_menus(self):
        dmm = DailyMenusManager()

        menu1 = DailyMenu(
            6, 12, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )
        menu2 = DailyMenu(
            6, 11, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )
        menu3 = DailyMenu(
            6, 10, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
        )

        assert len(dmm) == 0
        assert date(2019, 12, 6) not in dmm
        assert date(2019, 11, 6) not in dmm
        assert date(2019, 10, 6) not in dmm

        dmm.add_to_menus([menu1, menu2, menu3])
        assert len(dmm) == 3
        assert date(2019, 12, 6) in dmm
        assert date(2019, 11, 6) in dmm
        assert date(2019, 10, 6) in dmm

        dmm.add_to_menus([menu1, menu2, menu3])
        assert len(dmm) == 3
        assert date(2019, 12, 6) in dmm
        assert date(2019, 11, 6) in dmm
        assert date(2019, 10, 6) in dmm


@pytest.fixture
def load_mocks():
    std_mock = mock.patch(
        "app.menus.core.daily_menus_manager.DailyMenusManager.save_to_database"
    ).start()
    contains_mock = mock.patch(
        "app.menus.core.daily_menus_manager.DailyMenusManager.__contains__"
    ).start()
    lfd_mock = mock.patch(
        "app.menus.core.daily_menus_manager.DailyMenusManager.load_from_database",
        autospec=True,
    ).start()
    su_mock = mock.patch(
        "app.menus.core.daily_menus_manager.UpdateControl.should_update",
        spec_set=UpdateControl.should_update,
    ).start()
    parse_mock = mock.patch(
        "app.menus.core.daily_menus_manager.Parsers.parse", spec_set=Parsers.parse
    ).start()
    gmu_mock = mock.patch(
        "app.menus.core.daily_menus_manager.get_menus_urls", autospec=True
    ).start()
    gmu_mock.return_value = ["https://1.example.com", "https://2.example.com"]
    yield std_mock, contains_mock, lfd_mock, su_mock, parse_mock, gmu_mock

    mock.patch.stopall()


@pytest.fixture(params=[None, False, True])
def force(request):
    return request.param


@pytest.fixture(params=[True, False])
def today_in_database(request):
    return request.param


@pytest.fixture(params=[True, False])
def should_update(request):
    return request.param


def test_load(load_mocks, force, today_in_database, should_update, reset_database):
    std_mock, contains_mock, lfd_mock, su_mock, parse_mock, gmu_mock = load_mocks
    contains_mock.return_value = today_in_database
    su_mock.return_value = should_update

    will_update = force if force is not None else not today_in_database
    will_update = False if should_update is False else will_update

    DailyMenusManager.load(force=force)

    # Mocks
    contains_mock.assert_called_once_with(now().date())

    if will_update:
        gmu_mock.assert_called_once_with()
        std_mock.assert_called_once_with()
        parse_mock.assert_called()
        # gmu_mock returns 2 subdomains of example.com
        assert parse_mock.call_count == 2
    else:
        gmu_mock.assert_not_called()
        std_mock.assert_not_called()
        parse_mock.assert_not_called()


def test_to_json():
    dmm = DailyMenusManager()
    menu1 = DailyMenu(
        6, 12, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
    )
    menu2 = DailyMenu(
        6, 11, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
    )

    dmm.add_to_menus([menu1, menu2])

    expected_json = [
        {
            "id": 20191206,
            "day": "Viernes 6",
            "lunch": {"p1": "lunch-1", "p2": "lunch-2"},
            "dinner": {"p1": "dinner-1", "p2": "dinner-2"},
        },
        {
            "id": 20191106,
            "day": "Miércoles 6",
            "lunch": {"p1": "lunch-1", "p2": "lunch-2"},
            "dinner": {"p1": "dinner-1", "p2": "dinner-2"},
        },
    ]

    real_json = dmm.to_json()
    assert real_json == expected_json


@mock.patch(
    "app.menus.core.daily_menus_manager.DailyMenusDatabaseController.list_menus"
)
@mock.patch("app.menus.core.daily_menus_manager.DailyMenusManager.add_to_menus")
def test_load_from_database(atm_mock, list_menus_mock, client):

    menu = DailyMenu(
        1, 1, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
    )
    list_menus_mock.return_value = [menu, menu]

    dmm = DailyMenusManager()
    dmm.load_from_database()

    list_menus_mock.assert_called_once_with()
    atm_mock.assert_called_once()

    atm_mock.assert_has_calls([mock.call([menu, menu])], any_order=True)


@mock.patch("app.menus.core.daily_menus_manager.logger.debug", autospec=True)
@mock.patch(
    "app.menus.core.daily_menus_manager.UpdateControl.get_last_update", autospec=True
)
def test_save_to_database(glu_mock, debug_mock):
    glu_mock.return_value = "[info]"
    menu_mock = mock.Mock()
    menu_mock.to_string.return_value = "DailyMenu(mock)"

    dmm = DailyMenusManager()
    dmm.add_to_menus([menu_mock, menu_mock])
    dmm.save_to_database()

    menu_mock.to_database.assert_called()
    assert menu_mock.to_database.call_count == 2
    debug_mock.assert_called_with("Saving menus to database")
