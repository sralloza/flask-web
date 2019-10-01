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
        "app.menus.routes.get_last_menus_page", return_value="http://example.com"
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
            menu_mock.format_date.assert_called_with()
        else:
            assert menu_mock.format_date.call_count == 30
            menu_mock.format_date.assert_called_with(long=False)


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


@mock.patch("app.menus.routes.DailyMenusManager")
def test_menus_reload(dmm_mock, client):
    m = mock.Mock()
    dmm_mock.load.return_value.__iter__.return_value = iter([m, m, m, m, m])

    rv = client.get("/menus/reload")
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


@mock.patch("app.menus.routes.DailyMenusManager")
def test_today_reload(dmm_mock, client, menu_mock):
    dmm_mock.load.return_value.__iter__.return_value = iter(
        [menu_mock, menu_mock, menu_mock, menu_mock, menu_mock, menu_mock, menu_mock]
    )

    rv = client.get("/hoy/reload")
    assert rv.status_code == 302
    assert rv.location == "http://menus.sralloza.es/hoy"

    dmm_mock.load.assert_called_once_with(force=True)
    dmm_mock.load.return_value.__iter__.assert_called_once()
    menu_mock.to_database.assert_called()
    assert menu_mock.to_database.call_count == 7


@mock.patch("app.menus.core.daily_menus_manager.UpdateControl.should_update")
def test_today(su_mock, client):
    su_mock.return_value = False
    rv = client.get("/hoy")
    assert rv.status_code == 200
    assert b"menus.css" in rv.data
    assert b"loader.css" in rv.data
    assert b"getElementById" in rv.data
    assert b"today-js.js" in rv.data


class MenuApiDataCodes(Enum):
    good = 1
    exception = 2
    no_token = 3
    invalid_token = 4


ADD_MENU_API_DATA_GOOD = dict(
    day=1,
    month=1,
    year=2019,
    lunch1="lunch-1",
    lunch2="lunch2",
    dinner1="dinner-1",
    dinner2="dinner-2",
)
add_menu_api_data = (
    (ADD_MENU_API_DATA_GOOD, True, MenuApiDataCodes.good),
    (
        dict(
            day="X",
            month=1,
            year=2019,
            lunch1="lunch-1",
            lunch2="lunch-2",
            dinner1="dinner-1",
            dinner2="dinner-2",
        ),
        "ValueError: \"invalid literal for int() with base 10: 'X'\"",
        MenuApiDataCodes.exception,
    ),
    (
        dict(
            day=1,
            month="Y",
            year=2019,
            lunch1="lunch-1",
            lunch2="lunch-2",
            dinner1="dinner-1",
            dinner2="dinner-2",
        ),
        "ValueError: \"invalid literal for int() with base 10: 'Y'\"",
        MenuApiDataCodes.exception,
    ),
    (
        dict(
            day=1,
            month=1,
            year="Z",
            lunch1="lunch-1",
            lunch2="lunch-2",
            dinner1="dinner-1",
            dinner2="dinner-2",
        ),
        "ValueError: \"invalid literal for int() with base 10: 'Z'\"",
        MenuApiDataCodes.exception,
    ),
    (
        dict(
            day=1,
            month=1,
            year=2019,
            lunch2="lunch-2",
            dinner1="dinner-1",
            dinner2="dinner-2",
        ),
        "Missing 'lunch1'",
        MenuApiDataCodes.exception,
    ),
    (dict(), "Missing 'token'", MenuApiDataCodes.no_token),
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
            Meal(data["lunch1"], data["lunch2"]),
            Meal(data["dinner1"], data["dinner2"]),
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


@mock.patch("app.menus.routes.DailyMenusManager")
class TestApiMenus:
    def test_without_force(self, dmm_mock, client):
        menu = DailyMenu(
            28, 6, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
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
            }
        ] * 6

        rv = client.get("/api/menus")
        real_json = json.loads(rv.data.decode())

        assert rv.status_code == 200
        assert real_json == expected_json
        dmm_mock.load.assert_called_once_with(force=False)

    def test_with_force(self, dmm_mock, client):
        menu = DailyMenu(
            28, 6, 2019, Meal("lunch-1", "lunch-2"), Meal("dinner-1", "dinner-2")
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

    class PostDataType(Enum):
        good = None
        date_del = "date"
        date_change = "date"
        lunch_1_del = "lunch-1"
        lunch_1_change = "lunch-1"
        lunch_2_del = "lunch-2"
        lunch_2_change = "lunch-2"
        dinner_1_del = "dinner-1"
        dinner_1_change = "dinner-1"
        dinner_2_del = "dinner-2"
        dinner_2_change = "dinner-2"
        token_del = "token"
        token_change = "token"

        def is_change(self):
            return self.name.endswith("change")

        def is_del(self):
            return self.name.endswith("del")

    @pytest.fixture(params=PostDataType)
    def data_arg(self, request):
        return request.param

    @pytest.fixture
    def post_mocks(self):
        tm = mock.patch("app.menus.routes.gen_token", autospec=True).start()
        dmm = mock.patch("app.menus.routes.DailyMenusManager", autospec=True).start()

        yield tm, dmm

        mock.patch.stopall()

    def test_post(self, post_mocks, client, data_arg):
        token_mock, dmm_mock = post_mocks
        token_mock.return_value = "foo-token"

        post_data = self.POST_DATA_GOOD.copy()
        post_data["token"] = "foo-token"

        if data_arg == self.PostDataType.good:
            pass
        elif data_arg == self.PostDataType.date_change:
            post_data["date"] = "invalid-date"
        elif data_arg == self.PostDataType.date_del:
            del post_data['date']
        elif data_arg == self.PostDataType.token_change:
            post_data['token'] = 'invalid-token'
        elif data_arg == self.PostDataType.token_del:
            del post_data['token']
        elif data_arg == "invalid-token":
            post_data["token"] = "invalid-token"
        elif data_arg.is_change():
            post_data[data_arg.value] = ''
        elif data_arg.is_del():
            del post_data[data_arg.value]

        rv = client.post("/add", data=post_data)

        # Mocks
        if data_arg is self.PostDataType.good:
            # Everything ok, DMM called
            dmm_mock.load.assert_called_once_with(force=False)
            real_dmm_mock = dmm_mock.load.return_value
            real_dmm_mock.add_to_menus.assert_called_once()
            real_dmm_mock.save_to_database.assert_called_once_with()
        else:
            # Something went wrong, DMM not called
            dmm_mock.load.assert_not_called()
            real_dmm_mock = dmm_mock.load.return_value
            real_dmm_mock.add_to_menus.assert_not_called()
            real_dmm_mock.save_to_database.assert_not_called()

        # Data
        if data_arg is self.PostDataType.good:
            assert rv.status_code == 200
            assert b"Saved:\n<br>" in rv.data
            assert b"DailyMenu(" in rv.data
            assert b"meta http-equiv" in rv.data
        else:
            if data_arg == self.PostDataType.token_change:
                assert b"Invalid token" in rv.data
            elif data_arg == self.PostDataType.date_change:
                assert b"Invalid date" in rv.data
            else:
                assert f"{data_arg.value!r} is required".encode() in rv.data
            assert rv.status_code == 403