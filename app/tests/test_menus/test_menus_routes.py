import json
import re
from datetime import datetime
from unittest import mock

import pytest


@pytest.fixture
def menu_mock():
    m = mock.Mock()
    m.lunch.p1 = 'L1'
    m.lunch.p2 = 'L2'
    m.dinner.p1 = 'D1'
    m.dinner.p2 = 'D2'
    m.date.day = 1
    return m


class TestViewMenus:
    example_url = '<a href="http://example.com" target="_blank">Menús</a>'

    @pytest.fixture(params=[None, 'all', 'beta', 'all&beta'])
    def argument(self, request):
        return request.param

    @mock.patch('app.menus.routes.DailyMenusManager.load')
    @mock.patch('app.menus.routes.get_last_menus_page', return_value='http://example.com')
    def test_without_args(self, glmp_mock, load_mock, client, menu_mock, argument):
        menus_mocks = iter([menu_mock] * 30)
        # load_mock.return_value = menus_mocks
        load_mock.return_value.menus.__iter__.return_value = menus_mocks
        load_mock.return_value.menus.__getitem__.return_value = menus_mocks
        load_mock.menus = menus_mocks

        url = '/menus'
        if argument:
            url += '?' + argument
        rv = client.get(url)

        if argument == 'all&beta':
            assert rv.status_code == 301
            assert rv.location == 'http://menus.sralloza.es/menus?beta'
            load_mock.return_value.menus.__getitem__.assert_not_called()
            return

        assert rv.status_code == 200
        assert self.example_url.encode() in rv.data
        glmp_mock.assert_called_once_with()

        if argument is None:
            load_mock.return_value.menus.__getitem__.assert_called_with(slice(None, 15, None))
        else:
            load_mock.return_value.menus.__getitem__.assert_not_called()

        if argument is None:
            assert b'<a href="?all">Show all</a>' in rv.data

        if argument in (None, 'all'):
            assert b'table table-hover table-responsive table-striped' in rv.data
        elif argument == 'beta':
            assert b'href="//cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css' in rv.data
        else:
            assert 0, 'Invalid argument'

        menu_mock.format_date.assert_called()
        if argument in (None, 'all'):
            # Test before, with slice(None, 15, None)
            pass
        else:
            assert menu_mock.format_date.call_count == 30

            if argument == 'beta':
                menu_mock.format_date.assert_called_with(long=False)
            else:
                menu_mock.format_date.assert_called_with()


def test_redirect_menus(client):
    rv = client.get('/n')
    assert rv.status_code == 301
    assert rv.location == 'http://menus.sralloza.es/menus'

    rv = client.get('/new_menus')
    assert rv.status_code == 301
    assert rv.location == 'http://menus.sralloza.es/menus'

    rv = client.get('/new-menus')
    assert rv.status_code == 301
    assert rv.location == 'http://menus.sralloza.es/menus'


@mock.patch('app.menus.routes.DailyMenusManager')
def test_menus_reload(dmm_mock, client):
    m = mock.Mock()
    dmm_mock.load.return_value.__iter__.return_value = iter([m, m, m, m, m])

    rv = client.get('/menus/reload')
    assert rv.status_code == 302
    assert rv.location == 'http://menus.sralloza.es/menus'

    dmm_mock.load.assert_called_once_with(force=True)
    dmm_mock.load.return_value.__iter__.assert_called_once()
    m.to_database.assert_called()
    assert m.to_database.call_count == 5


def test_today_redirect(client):
    rv = client.get('/h')
    assert rv.status_code == 301
    assert rv.location == 'http://menus.sralloza.es/hoy'


@mock.patch('app.menus.routes.DailyMenusManager')
def test_today_reload(dmm_mock, client, menu_mock):
    dmm_mock.load.return_value.__iter__.return_value = iter(
        [menu_mock, menu_mock, menu_mock, menu_mock, menu_mock, menu_mock, menu_mock])

    rv = client.get('/hoy/reload')
    assert rv.status_code == 302
    assert rv.location == 'http://menus.sralloza.es/hoy'

    dmm_mock.load.assert_called_once_with(force=True)
    dmm_mock.load.return_value.__iter__.assert_called_once()
    menu_mock.to_database.assert_called()
    assert menu_mock.to_database.call_count == 7


class TestToday:
    disabled_yesterday_pattern = re.compile(
        r'<a class="btn btn-primary disabled" href="None"\s+role="button">\s+Anterior\s+</a>')
    disabled_tomorrow_pattern = re.compile(
        r'<a class="btn btn-primary disabled" href="None"\s+role="button">\s+Siguiente\s+</a>')
    example_link = '<a href="http://example.com" target="_blank">'

    @pytest.fixture
    def today_dt(self):
        return datetime(2019, 1, 1)

    @pytest.fixture
    def today_mocks(self):
        dmm_mock = mock.patch('app.menus.routes.DailyMenusManager').start()
        today_mock = mock.patch('app.menus.routes.today').start()
        search_mock = mock.patch('re.search').start()
        glmp_mock = mock.patch('app.menus.routes.get_last_menus_page',
                               return_value='http://example.com').start()
        daily_menu_mock = mock.patch('app.menus.routes.DailyMenu').start()

        yield dmm_mock, today_mock, search_mock, glmp_mock, daily_menu_mock

        mock.patch.stopall()

    @pytest.fixture(params=[None, '2019-2-1', '2019-5-1', 'invalid'])
    def day_request(self, request):
        return request.param

    @pytest.fixture(params=['none', 'yesterday', 'tomorrow', 'both'])
    def db_available(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def is_empty(self, request):
        return request.param

    def test_today(self, today_mocks, client, menu_mock, today_dt, day_request, db_available,
                   is_empty):
        dmm_mock, today_mock, search_mock, glmp_mock, daily_menu_mock = today_mocks

        daily_menu_mock.return_value = menu_mock

        dmm_mock.load.return_value.__getitem__.return_value = menu_mock
        menu_mock.is_empty.return_value = is_empty

        today_mock.return_value = today_dt
        search_mock.return_value.group.return_value.capitalize.return_value = 'Martes'

        if db_available == 'none':
            dmm_mock.load.return_value.__contains__.return_value = False
        elif db_available == 'yesterday':
            dmm_mock.load.return_value.__contains__.side_effect = iter([True, False])
        elif db_available == 'tomorrow':
            dmm_mock.load.return_value.__contains__.side_effect = iter([False, True])
        elif db_available == 'both':
            dmm_mock.load.return_value.__contains__.return_value = True

        get_url = '/hoy'
        if day_request:
            get_url += '?day=' + day_request

        rv = client.get(get_url)

        assert self.example_link.encode() in rv.data

        # If given an invalid day in the request, 404 should be returned
        if day_request == 'invalid':
            assert rv.status_code == 404
        else:
            assert rv.status_code == 200

        if is_empty:
            assert b'Datos no disponibles' in rv.data
        else:
            assert b'Martes 1' in rv.data
            assert b'Comida' in rv.data
            assert b'Cena' in rv.data
            assert b'L1' in rv.data
            assert b'L2' in rv.data
            assert b'D1' in rv.data
            assert b'D2' in rv.data

        if db_available == 'none':
            assert TestToday.disabled_yesterday_pattern.search(rv.data.decode())
            assert TestToday.disabled_tomorrow_pattern.search(rv.data.decode())
        elif db_available == 'yesterday':
            assert not TestToday.disabled_yesterday_pattern.search(rv.data.decode())
            assert TestToday.disabled_tomorrow_pattern.search(rv.data.decode())
        elif db_available == 'tomorrow':
            assert TestToday.disabled_yesterday_pattern.search(rv.data.decode())
            assert not TestToday.disabled_tomorrow_pattern.search(rv.data.decode())
        elif db_available == 'both':
            assert not TestToday.disabled_yesterday_pattern.search(rv.data.decode())
            assert not TestToday.disabled_tomorrow_pattern.search(rv.data.decode())
        else:
            assert 0, 'Invalid state'

        if day_request == 'invalid':
            today_mock.assert_called_once_with()
            dmm_mock.load.return_value.__getitem__.assert_not_called()
        elif not day_request:
            # If a date is passed in the request, datetime.now() should not be called
            today_mock.assert_called_once_with()
            dmm_mock.load.return_value.__getitem__.assert_called_with(today_dt.date())
        else:
            dmm_mock.load.return_value.__getitem__.assert_called_with(
                datetime.strptime(day_request, '%Y-%m-%d').date())
            today_mock.assert_not_called()

        if day_request == 'invalid':
            daily_menu_mock.assert_called_once_with(today_dt.day, today_dt.month, today_dt.year)
        else:
            daily_menu_mock.assert_not_called()

        menu_mock.is_empty.assert_called_once_with()
        glmp_mock.assert_called_once_with()
        search_mock.assert_called_once()
        search_mock.return_value.group.assert_called_once_with(1)
        search_mock.return_value.group.return_value.capitalize.assert_called_once_with()


@mock.patch('re.search')
@mock.patch('app.menus.routes.DailyMenusManager')
def test_api_menus(dmm_mock, search_mock, client, menu_mock):
    menu_mock.format_date.return_value = '28 de junio de 2019 (viernes)'
    menu_mock.date.day = 28

    dmm_mock.load.return_value.__iter__.return_value = iter(
        [menu_mock, menu_mock, menu_mock, menu_mock, menu_mock])
    search_mock.return_value.group.return_value.capitalize.return_value = 'Viernes'

    expected_json = [{'day': 'Viernes 28', 'lunch': {'p1': 'L1', 'p2': 'L2'},
                      'dinner': {'p1': 'D1', 'p2': 'D2'}}] * 5

    rv = client.get('/api/menus')

    assert rv.status_code == 200
    assert json.loads(rv.data.decode()) == expected_json

    search_mock.return_value.group.assert_called_with(1)
    assert search_mock.return_value.group.call_count == 5

    search_mock.return_value.group.return_value.capitalize.assert_called()
    assert search_mock.return_value.group.return_value.capitalize.call_count == 5

    menu_mock.format_date.assert_called()
    assert menu_mock.format_date.call_count == 5
