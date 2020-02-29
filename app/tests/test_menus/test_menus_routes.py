import json
import string
from enum import Enum
from random import choice
from unittest import mock

import pytest

from app.menus.core.daily_menus_manager import DailyMenusManager
from app.menus.core.structure import DailyMenu, Meal
from app.utils import now


@pytest.fixture
def menu_mock():
    m = mock.Mock()
    m.lunch.p1 = "lunch-1"
    m.lunch.p2 = "lunch-2"
    m.dinner.p1 = "dinner-1"
    m.dinner.p2 = "dinner-2"
    m.date.day = 1
    return m


class TestMenusView:
    example_url = '<a href="http://example.com" target="_blank">Menús</a>'

    @pytest.fixture(params=[None, "all", "beta", "all&beta"])
    def argument(self, request):
        return request.param

    @mock.patch("app.menus.routes.DailyMenusManager.load")
    @mock.patch(
        "app.menus.routes.get_last_menus_page",
        return_value="http://example.com",
        autospec=True,
    )
    def test_without_args(self, glmp_mock, load_mock, client, menu_mock, argument):
        menus_mocks = iter([menu_mock] * 30)
        load_mock.return_value.menus.__iter__.return_value = menus_mocks
        load_mock.return_value.menus.__getitem__.return_value = menus_mocks
        load_mock.menus = menus_mocks

        url = "/menus"
        if argument:
            url += "?" + argument
        rv = client.get(url)

        if argument == "all&beta":
            assert rv.status_code == 302
            assert rv.location == "http://menus.sralloza.es/menus?beta"
            load_mock.return_value.menus.__getitem__.assert_not_called()
            menu_mock.format_date.assert_not_called()
            glmp_mock.assert_not_called()
            return

        assert rv.status_code == 200
        assert self.example_url.encode() in rv.data
        glmp_mock.assert_called_once_with()

        if argument is None:
            load_mock.return_value.menus.__getitem__.assert_called_with(
                slice(None, 15, None)
            )
        else:
            load_mock.return_value.menus.__getitem__.assert_not_called()

        if argument is None:
            assert b'<a href="?all">Show all</a>' in rv.data

        if argument in (None, "all"):
            assert b"table table-hover table-responsive table-striped" in rv.data
        elif argument == "beta":
            assert (
                b'href="//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css'
                in rv.data
            )

        menu_mock.format_date.assert_called()
        if argument in (None, "all"):
            # Test before, with slice(None, 15, None)
            # For some reason, in testing context is passed as an arg as well
            assert menu_mock.format_date.call_args[1] == {}
        else:
            assert menu_mock.format_date.call_count == 30
            # For some reason, in testing context is passed as an arg as well
            assert menu_mock.format_date.call_args[1] == {"long": False}


def test_menus_redirect(client):
    rv = client.get("/n")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/menus"

    rv = client.get("/new_menus")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/menus"

    rv = client.get("/new-menus")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/menus"

def test_do_not_use_force_or_reload(client):
    assert client.get("/menus/reload").status_code == 404
    assert client.get("/hoy/reload").status_code == 404

@mock.patch("app.menus.routes.DailyMenusManager", autospec=True)
def test_menus_update(dmm_mock, client):
    m = mock.Mock()
    dmm_mock.load.return_value.__iter__.return_value = iter([m, m, m, m, m])

    rv = client.get("/menus/update")
    assert rv.status_code == 302
    assert rv.location == "http://menus.sralloza.es/menus"

    dmm_mock.load.assert_called_once_with(force=True)
    dmm_mock.load.return_value.__iter__.assert_called_once()
    m.to_database.assert_called()
    assert m.to_database.call_count == 5


def test_today_redirect(client):
    rv = client.get("/h")
    assert rv.status_code == 301
    assert rv.location == "http://menus.sralloza.es/hoy"


@mock.patch("app.menus.routes.DailyMenusManager", autospec=True)
def test_today_update(dmm_mock, client, menu_mock):
    dmm_mock.load.return_value.__iter__.return_value = iter(
        [menu_mock, menu_mock, menu_mock, menu_mock, menu_mock, menu_mock, menu_mock]
    )

    rv = client.get("/hoy/update")
    assert rv.status_code == 302
    assert rv.location == "http://menus.sralloza.es/hoy?update"

    dmm_mock.load.assert_not_called()
    dmm_mock.load.return_value.__iter__.assert_not_called()
    menu_mock.to_database.assert_not_called()


@mock.patch("app.menus.core.daily_menus_manager.UpdateControl.should_update")
def test_today(su_mock, client, reset_database):
    su_mock.return_value = False
    rv = client.get("/hoy")
    assert rv.status_code == 200
    assert b"menus.css" in rv.data
    assert b"loader.css" in rv.data
    assert b"getElementById" in rv.data
    assert b"today.js" in rv.data


class MenuApiDataCodes(Enum):
    good = 1
    exception = 2
    no_token = 3
    invalid_token = 4


ADD_MENU_API_DATA_GOOD = {
    "day": 1,
    "month": 1,
    "year": 2019,
    "lunch-1": "lunch-1",
    "lunch-2": "lunch-2",
    "dinner-1": "dinner-1",
    "dinner-2": "dinner-2",
}
add_menu_api_data = (
    (ADD_MENU_API_DATA_GOOD, True, MenuApiDataCodes.good),
    (
        {
            "day": "X",
            "month": 1,
            "year": 2019,
            "lunch-1": "lunch-1",
            "lunch-2": "lunch-2",
            "dinner-1": "dinner-1",
            "dinner-2": "dinner-2",
        },
        "ValueError: \"invalid literal for int() with base 10: 'X'\"",
        MenuApiDataCodes.exception,
    ),
    (
        {
            "day": 1,
            "month": "Y",
            "year": 2019,
            "lunch-1": "lunch-1",
            "lunch-2": "lunch-2",
            "dinner-1": "dinner-1",
            "dinner-2": "dinner-2",
        },
        "ValueError: \"invalid literal for int() with base 10: 'Y'\"",
        MenuApiDataCodes.exception,
    ),
    (
        {
            "day": 1,
            "month": 1,
            "year": "Z",
            "lunch-1": "lunch-1",
            "lunch-2": "lunch-2",
            "dinner-1": "dinner-1",
            "dinner-2": "dinner-2",
        },
        "ValueError: \"invalid literal for int() with base 10: 'Z'\"",
        MenuApiDataCodes.exception,
    ),
    (
        {
            "day": 1,
            "month": 1,
            "year": 2019,
            "lunch-1": None,
            "lunch-2": "lunch-2",
            "dinner-1": "dinner-1",
            "dinner-2": "dinner-2",
        },
        True,
        MenuApiDataCodes.good,
    ),
    (
        {
            "day": 1,
            "month": 1,
            "year": 2019,
            "lunch-1": "lunch-1",
            "lunch-2": None,
            "dinner-1": "dinner-1",
            "dinner-2": "dinner-2",
        },
        True,
        MenuApiDataCodes.good,
    ),
    (
        {
            "day": 1,
            "month": 1,
            "year": 2019,
            "lunch-1": "lunch-1",
            "lunch-2": "lunch-2",
            "dinner-1": None,
            "dinner-2": "dinner-2",
        },
        True,
        MenuApiDataCodes.good,
    ),
    (
        {
            "day": 1,
            "month": 1,
            "year": 2019,
            "lunch-1": "lunch-1",
            "lunch-2": "lunch-2",
            "dinner-1": "dinner-1",
            "dinner-2": None,
        },
        True,
        MenuApiDataCodes.good,
    ),
    (dict(), "'token' is required (None)", MenuApiDataCodes.no_token),
    (ADD_MENU_API_DATA_GOOD, "Invalid token", MenuApiDataCodes.invalid_token),
)


@pytest.mark.parametrize("data, exception, code", add_menu_api_data)
def test_add_menu_api(client, data, exception, code):
    url = "/api/menus/add"

    try:
        menu = DailyMenu(
            data["day"],
            data["month"],
            data["year"],
            Meal(data["lunch-1"], data["lunch-2"]),
            Meal(data["dinner-1"], data["dinner-2"]),
        )
    except (TypeError, KeyError):
        menu = DailyMenu(1, 1, 2010)

    if code is not MenuApiDataCodes.no_token:
        data["token"] = now().strftime("%Y%m%d%H%M")

    if code is MenuApiDataCodes.invalid_token:
        data["token"] = "".join([choice(string.digits) for _ in range(8)])

    rv = client.post(url, data=data)
    rv_data = rv.data.decode()

    if code is MenuApiDataCodes.good:
        assert repr(menu) == rv_data
    else:
        assert exception in rv_data


@mock.patch("app.menus.routes.DailyMenusManager", autospec=True)
class TestApiMenus:
    def test_without_force(self, dmm_mock, client):
        url = "https://example.com"
        menu = DailyMenu(
            28, 6, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2"), url,
        )

        dmm = DailyMenusManager()
        dmm.menus = [menu] * 6
        dmm_mock.load.return_value = dmm

        expected_json = [
            {
                "id": 20190628,
                "day": "Viernes 28",
                "lunch": {"p1": "lunch-1", "p2": "lunch-2"},
                "dinner": {"p1": "dinner-1", "p2": "dinner-2"},
                "url": "https://example.com",
            }
        ] * 6

        rv = client.get("/api/menus")
        real_json = json.loads(rv.data.decode())

        assert rv.status_code == 200
        assert real_json == expected_json
        dmm_mock.load.assert_called_once_with(force=False)

    def test_with_force(self, dmm_mock, client):
        url = "https://example.com"
        menu = DailyMenu(
            28, 6, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2"), url,
        )

        dmm = DailyMenusManager()
        dmm.menus = [menu] * 6
        dmm_mock.load.return_value = dmm

        expected_json = [
            {
                "id": 20190628,
                "day": "Viernes 28",
                "lunch": {"p1": "lunch-1", "p2": "lunch-2"},
                "dinner": {"p1": "dinner-1", "p2": "dinner-2"},
                "url": "https://example.com",
            }
        ] * 6

        rv = client.get("/api/menus?force")
        real_json = json.loads(rv.data.decode())

        assert rv.status_code == 200
        assert real_json == expected_json
        dmm_mock.load.assert_called_once_with(force=True)


class TestAddMenuInterface:
    def test_get(self, client):
        rv = client.get("/add")

        assert b"form" in rv.data
        assert rv.data.count(b"<h5") == 1  # One title
        assert rv.data.count(b"</h5") == 1  # One title

        # 6 inputs (1xdate, 2xlunch, 2xdinner, 1xtoken)
        assert rv.data.count(b'<div class="form-group">') == 6
        assert rv.data.count(b"placeholder") == 6
        assert rv.data.count(b"<label") == 6
        assert rv.data.count(b"</label") == 6
        assert rv.data.count(b"<input") == 6

        # 2 button (submit and reset)
        assert rv.data.count(b"<button") == 2
        assert rv.data.count(b"</button") == 2

        # Texts
        assert "Añadir datos".encode() in rv.data  # Title
        assert b"Comida - 1" in rv.data
        assert b"Comida - 2" in rv.data
        assert b"Cena - 1" in rv.data
        assert b"Cena - 2" in rv.data
        assert b"Token" in rv.data

    POST_DATA_GOOD = {
        "date": "2000-12-31",
        "lunch-1": "l1",
        "lunch-2": "l2",
        "dinner-1": "d1",
        "dinner-2": "d2",
    }

    class ActionType(Enum):
        delete = "delete"
        change = "change"

    class PostDataType(Enum):
        good = None
        date = "date"
        lunch_1 = "lunch-1"
        lunch_2 = "lunch-2"
        dinner_1 = "dinner-1"
        dinner_2 = "dinner-2"
        token = "token"

        def is_meal(self):
            return self in (
                self.__class__.lunch_1,
                self.__class__.lunch_2,
                self.__class__.dinner_1,
                self.__class__.dinner_2,
            )

    @pytest.fixture(params=PostDataType)
    def data_type(self, request):
        return request.param

    @pytest.fixture(params=ActionType)
    def action_type(self, request):
        return request.param

    @mock.patch("app.utils.Tokens.gen_tokens")
    def test_post(self, token_mock, client, data_type, action_type, reset_database):
        token_mock.return_value = ["foo-token"]

        post_data = self.POST_DATA_GOOD.copy()
        post_data["token"] = "foo-token"

        if data_type == self.PostDataType.good:
            pass
        elif action_type == self.ActionType.change:
            if data_type == self.PostDataType.date:
                post_data["date"] = "invalid-date"
            elif data_type == self.PostDataType.token:
                post_data["token"] = "invalid-token"
            else:
                post_data[data_type.value] = ""
        elif action_type == self.ActionType.delete:
            del post_data[data_type.value]

        rv = client.post("/add", data=post_data)

        # Meals (lunch1, lunch2, dinner1 and dinner2) are not required
        if data_type is self.PostDataType.good or data_type.is_meal():
            assert rv.status_code == 200
            assert b"Saved:\n<br>" in rv.data
            assert b"DailyMenu(" in rv.data
            assert b"meta http-equiv" in rv.data
            assert b"Home" in rv.data
            assert b"Add more" in rv.data
            assert b"href" in rv.data
        else:
            if action_type == self.ActionType.change:
                if data_type == self.PostDataType.date:
                    assert b"Invalid date" in rv.data
                elif data_type == self.PostDataType.token:
                    assert b"Invalid token" in rv.data
            elif action_type == self.ActionType.delete:
                assert f"{data_type.value!r} is required".encode() in rv.data

            assert rv.status_code == 403

    @mock.patch("app.utils.Tokens.gen_tokens")
    def test_post_repeating_date(self, token_mock, client, reset_database):
        token_mock.return_value = ["foo-token"]

        post_data = self.POST_DATA_GOOD.copy()
        post_data["token"] = "foo-token"

        rv = client.post("/add", data=post_data)
        assert rv.status_code == 200
        assert b"Saved" in rv.data
        assert b"Not saved" not in rv.data

        rv = client.post("/add", data=post_data)
        assert rv.status_code == 409
        assert b"Saved" not in rv.data
        assert b"Not saved" in rv.data


class TestDelMenuInterface:
    def test_get(self, client):
        rv = client.get("/del")

        assert b"form" in rv.data
        assert rv.data.count(b"<h5") == 1  # One title
        assert rv.data.count(b"</h5") == 1  # One title

        # 2 inputs (1xdate, 1xtoken)
        assert rv.data.count(b'<div class="form-group">') == 2
        assert rv.data.count(b"placeholder") == 2
        assert rv.data.count(b"<label") == 2
        assert rv.data.count(b"</label") == 2
        assert rv.data.count(b"<input") == 2

        # 2 button (submit and reset)
        assert rv.data.count(b"<button") == 2
        assert rv.data.count(b"</button") == 2

        # Texts
        assert b"Eliminar datos" in rv.data  # Title
        assert b"Comida - 1" not in rv.data  # Check against /add
        assert b"Comida - 2" not in rv.data  # Check against /add
        assert b"Cena - 1" not in rv.data  # Check against /add
        assert b"Cena - 2" not in rv.data  # Check against /add
        assert b"Token" in rv.data

    POST_DATA_GOOD = {"date": "2000-12-31"}

    class ActionType(Enum):
        good = "good"
        invalid_token = "invalid_token"
        missing_token = "missing_token"
        missing_date = "missing_date"
        invalid_date = "invalid_date"

    @pytest.fixture(params=ActionType)
    def action(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def is_ok(self, request):
        return request.param

    @mock.patch("app.menus.routes.DailyMenu.remove_from_database", autospec=True)
    @mock.patch("app.utils.Tokens.gen_tokens")
    def test_post(self, token_mock, rfd_mock, is_ok, client, action, reset_database):
        rfd_mock.return_value = is_ok
        token_mock.return_value = ["foo-token"]

        post_data = self.POST_DATA_GOOD.copy()
        post_data["token"] = "foo-token"

        if action is self.ActionType.good:
            pass
        elif action is self.ActionType.invalid_token:
            post_data["token"] = "invalid token"
        elif action is self.ActionType.missing_token:
            del post_data["token"]
        elif action is self.ActionType.invalid_date:
            post_data["date"] = "invalid date"
        elif action is self.ActionType.missing_date:
            del post_data["date"]

        rv = client.post("/del", data=post_data)

        # Data
        if action is self.ActionType.good:
            if is_ok:
                assert b"Deleted:\n<br>" in rv.data
                assert rv.status_code == 200
            else:
                assert b"Not deleted:\n<br>" in rv.data
                assert rv.status_code == 409
            assert b"meta http-equiv" in rv.data
            assert b"Home" in rv.data
            assert b"Del more" in rv.data
            assert b"href" in rv.data
        else:
            assert rv.status_code == 403
        if action is self.ActionType.invalid_token:
            assert b"Invalid token" in rv.data
        elif action is self.ActionType.missing_token:
            assert b"'token' is required" in rv.data
        elif action is self.ActionType.invalid_date:
            assert b"Invalid date" in rv.data
        elif action is self.ActionType.missing_date:
            assert b"'date' is required" in rv.data
