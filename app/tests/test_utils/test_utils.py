from pathlib import Path
from unittest import mock

import pytest
from requests.exceptions import ConnectionError

from app.utils import get_last_menus_page
from app.utils import PRINCIPAL_URL


@mock.patch('requests.get')
@mock.patch('app.utils.logger')
class TestGetMenusUrls:
    url_expected = 'https://www.residenciasantiago.es/2019/06/20/del-21-al-24-de-junio-2019/'

    warning_expected = 'Connection error downloading principal url (%r) (%d retries left)'

    @pytest.fixture(scope='class')
    def test_content(self):
        path = Path(__file__).parent.parent / 'data' / 'get_urls.txt'

        with path.open() as f:
            return f.read()

    def test_ok(self, logger_mock, requests_get_mock, test_content):
        requests_get_mock.return_value.text = test_content
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with('Getting last menus url')
        assert url == self.url_expected

    def test_one_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter([ConnectionError, foo_mock])
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with('Getting last menus url')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4)
        ])
        assert url == self.url_expected

    def test_two_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter([ConnectionError, ConnectionError, foo_mock])
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with('Getting last menus url')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4),
            mock.call(self.warning_expected, PRINCIPAL_URL, 3),
        ])
        assert logger_mock.warning.call_count == 2
        assert url == self.url_expected

    def test_three_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, foo_mock])
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with('Getting last menus url')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4),
            mock.call(self.warning_expected, PRINCIPAL_URL, 3),
            mock.call(self.warning_expected, PRINCIPAL_URL, 2),
        ])
        assert logger_mock.warning.call_count == 3
        assert url == self.url_expected

    def test_four_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, ConnectionError, foo_mock])
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with('Getting last menus url')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4),
            mock.call(self.warning_expected, PRINCIPAL_URL, 3),
            mock.call(self.warning_expected, PRINCIPAL_URL, 2),
            mock.call(self.warning_expected, PRINCIPAL_URL, 1),
        ])
        assert logger_mock.warning.call_count == 4
        assert url == self.url_expected

    def test_five_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, ConnectionError, ConnectionError,
             foo_mock])
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with('Getting last menus url')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4),
            mock.call(self.warning_expected, PRINCIPAL_URL, 3),
            mock.call(self.warning_expected, PRINCIPAL_URL, 2),
            mock.call(self.warning_expected, PRINCIPAL_URL, 1),
            mock.call(self.warning_expected, PRINCIPAL_URL, 0),
        ])
        assert logger_mock.warning.call_count == 5

        logger_mock.critical.assert_called_once_with(
            'Fatal connection error downloading principal url (%r) (%d retries)',
            PRINCIPAL_URL, 5)

        assert url == PRINCIPAL_URL
