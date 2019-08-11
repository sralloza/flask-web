from pathlib import Path
from unittest import mock

import pytest
from requests.exceptions import ConnectionError

from app.menus.core.utils import get_menus_urls, PRINCIPAL_URL, Worker


@mock.patch('requests.get')
@mock.patch('app.menus.core.get_urls.logger')
class TestGetMenusUrls:
    urls_expected = ['https://www.residenciasantiago.es/2019/06/20/del-21-al-24-de-junio-2019/',
                     'https://www.residenciasantiago.es/2019/06/17/del-18-al-20-de-junio-2019/']

    warning_expected = 'Connection error downloading principal url (%r) (%d retries left)'

    @pytest.fixture(scope='class')
    def test_content(self):
        path = Path(__file__).parent.parent / 'data' / 'get_urls.txt'

        with path.open() as f:
            return f.read()

    def test_ok(self, logger_mock, requests_get_mock, test_content):
        requests_get_mock.return_value.text = test_content
        urls = get_menus_urls()

        logger_mock.debug.assert_called_once_with('Getting menus urls')
        assert len(urls) == 2
        assert urls == self.urls_expected

    def test_one_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter([ConnectionError, foo_mock])
        urls = get_menus_urls()

        logger_mock.debug.assert_called_once_with('Getting menus urls')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4)
        ])
        assert len(urls) == 2
        assert urls == self.urls_expected

    def test_two_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter([ConnectionError, ConnectionError, foo_mock])
        urls = get_menus_urls()

        logger_mock.debug.assert_called_once_with('Getting menus urls')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4),
            mock.call(self.warning_expected, PRINCIPAL_URL, 3),
        ])
        assert logger_mock.warning.call_count == 2
        assert len(urls) == 2
        assert urls == self.urls_expected

    def test_three_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, foo_mock])
        urls = get_menus_urls()

        logger_mock.debug.assert_called_once_with('Getting menus urls')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4),
            mock.call(self.warning_expected, PRINCIPAL_URL, 3),
            mock.call(self.warning_expected, PRINCIPAL_URL, 2),
        ])
        assert logger_mock.warning.call_count == 3
        assert len(urls) == 2
        assert urls == self.urls_expected

    def test_four_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, ConnectionError, foo_mock])
        urls = get_menus_urls()

        logger_mock.debug.assert_called_once_with('Getting menus urls')
        logger_mock.warning.assert_has_calls([
            mock.call(self.warning_expected, PRINCIPAL_URL, 4),
            mock.call(self.warning_expected, PRINCIPAL_URL, 3),
            mock.call(self.warning_expected, PRINCIPAL_URL, 2),
            mock.call(self.warning_expected, PRINCIPAL_URL, 1),
        ])
        assert logger_mock.warning.call_count == 4
        assert len(urls) == 2
        assert urls == self.urls_expected

    def test_five_connection_error(self, logger_mock, requests_get_mock, test_content):
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, ConnectionError, ConnectionError,
             foo_mock])
        urls = get_menus_urls()

        logger_mock.debug.assert_called_once_with('Getting menus urls')
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

        assert len(urls) == 0
        assert urls == []


@pytest.mark.skip
def test_has_day():
    pass


@pytest.mark.skip
def test_filter_data():
    pass


@pytest.mark.skip
class TestPatterns:
    def test_day_pattern(self):
        pass

    def test_semi_day_pattern_1(self):
        pass

    def test_semi_day_pattern_2(self):
        pass

    def test_fix_dates_patterns_1(self):
        pass

    def test_fix_dates_patterns_2(self):
        pass

    def test_ignore_patterns(self):
        pass


@pytest.mark.skip('Check')
class TestWorker:
    @mock.patch('app.menus.core.logger.debug', spec=True)
    def test_run(self, logger_mock):
        m = mock.Mock()
        w = Worker('http://example.com', m)

        w.run()

        logger_mock.assert_called_once_with('Starting worker with url %s', 'http://example.com')
        m.process_url.assert_called_once_with('http://example.com', 5)
