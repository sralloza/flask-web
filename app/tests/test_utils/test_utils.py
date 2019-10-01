from pathlib import Path
from unittest import mock

import pytest
from requests.exceptions import ConnectionError

from app.utils import (PRINCIPAL_URL, Translator, _Cache, gen_token,
                       get_last_menus_page, get_post_arg)


@mock.patch("requests.get", autospec=True)
@mock.patch("app.utils.logger", autospec=True)
class TestGetLastMenusPage:
    url_expected = (
        "https://www.residenciasantiago.es/2019/06/20/del-21-al-24-de-junio-2019/"
    )

    warning_expected = (
        "Connection error downloading principal url (%r) (%d retries left)"
    )

    @pytest.fixture(scope="class")
    def test_content(self):
        path = Path(__file__).parent.parent / "data" / "get_urls.txt"

        with path.open() as f:
            return f.read()

    def test_ok(self, logger_mock, requests_get_mock, test_content):
        requests_get_mock.return_value.text = test_content
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with("Getting last menus url")
        assert url == self.url_expected

    @mock.patch("app.utils._Cache", autospec=True)
    def test_one_connection_error(
        self, static_mock, logger_mock, requests_get_mock, test_content
    ):
        static_mock.redirect_url = None
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter([ConnectionError, foo_mock])
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with("Getting last menus url")
        logger_mock.warning.assert_has_calls(
            [mock.call(self.warning_expected, PRINCIPAL_URL, 4)]
        )
        assert url == self.url_expected

    @mock.patch("app.utils._Cache", autospec=True)
    def test_two_connection_error(
        self, static_mock, logger_mock, requests_get_mock, test_content
    ):
        static_mock.redirect_url = None
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, foo_mock]
        )
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with("Getting last menus url")
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_expected, PRINCIPAL_URL, 4),
                mock.call(self.warning_expected, PRINCIPAL_URL, 3),
            ]
        )
        assert logger_mock.warning.call_count == 2
        assert url == self.url_expected

    @mock.patch("app.utils._Cache", autospec=True)
    def test_three_connection_error(
        self, static_mock, logger_mock, requests_get_mock, test_content
    ):
        static_mock.redirect_url = None
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, foo_mock]
        )
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with("Getting last menus url")
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_expected, PRINCIPAL_URL, 4),
                mock.call(self.warning_expected, PRINCIPAL_URL, 3),
                mock.call(self.warning_expected, PRINCIPAL_URL, 2),
            ]
        )
        assert logger_mock.warning.call_count == 3
        assert url == self.url_expected

    @mock.patch("app.utils._Cache", autospec=True)
    def test_four_connection_error(
        self, static_mock, logger_mock, requests_get_mock, test_content
    ):
        static_mock.redirect_url = None
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [
                ConnectionError,
                ConnectionError,
                ConnectionError,
                ConnectionError,
                foo_mock,
            ]
        )
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with("Getting last menus url")
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_expected, PRINCIPAL_URL, 4),
                mock.call(self.warning_expected, PRINCIPAL_URL, 3),
                mock.call(self.warning_expected, PRINCIPAL_URL, 2),
                mock.call(self.warning_expected, PRINCIPAL_URL, 1),
            ]
        )
        assert logger_mock.warning.call_count == 4
        assert url == self.url_expected

    @mock.patch("app.utils._Cache", autospec=True)
    def test_five_connection_error(
        self, static_mock, logger_mock, requests_get_mock, test_content
    ):
        static_mock.redirect_url = None
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.side_effect = iter(
            [
                ConnectionError,
                ConnectionError,
                ConnectionError,
                ConnectionError,
                ConnectionError,
                foo_mock,
            ]
        )
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with("Getting last menus url")
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_expected, PRINCIPAL_URL, 4),
                mock.call(self.warning_expected, PRINCIPAL_URL, 3),
                mock.call(self.warning_expected, PRINCIPAL_URL, 2),
                mock.call(self.warning_expected, PRINCIPAL_URL, 1),
                mock.call(self.warning_expected, PRINCIPAL_URL, 0),
            ]
        )
        assert logger_mock.warning.call_count == 5

        logger_mock.critical.assert_called_once_with(
            "Fatal connection error downloading principal url (%r) (%d retries)",
            PRINCIPAL_URL,
            5,
        )

        assert url == PRINCIPAL_URL

    def test_use_cache(self, logger_mock, requests_get_mock, test_content):
        _Cache.redirect_url = None
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        requests_get_mock.return_value = foo_mock
        url = get_last_menus_page()

        logger_mock.debug.assert_called_once_with("Getting last menus url")
        assert url == self.url_expected

        url2 = get_last_menus_page()
        assert url2 == self.url_expected
        assert logger_mock.debug.call_count == 1
        assert requests_get_mock.call_count == 1


class TestTranslator:
    esp_eng = (
        ("12 febrero 2016 martes", "12 february 2016 tuesday"),
        ("13 de diciembre de 2016 (martes)", "13 de december de 2016 (tuesday)"),
        ("13 de diciembre de 2017 (miércoles)", "13 de december de 2017 (wednesday)"),
        ("13 de enero de 2017 (viernes)", "13 de january de 2017 (friday)"),
        ("14 de julio de 2017 (viernes)", "14 de july de 2017 (friday)"),
        ("15 de agosto de 2017 (martes)", "15 de august de 2017 (tuesday)"),
        ("16 de octubre de 2017 (lunes)", "16 de october de 2017 (monday)"),
        ("16 enero viernes", "16 january friday"),
        ("22 de septiembre de 2017 (viernes)", "22 de september de 2017 (friday)"),
        ("23 de febrero de 2017 (jueves)", "23 de february de 2017 (thursday)"),
        ("28 de junio de 2017 (miércoles)", "28 de june de 2017 (wednesday)"),
        ("30 de mayo de 2017 (martes)", "30 de may de 2017 (tuesday)"),
        ("6 de marzo de 2017 (lunes)", "6 de march de 2017 (monday)"),
        ("7 de noviembre de 2017 (martes)", "7 de november de 2017 (tuesday)"),
        ("9 de abril de 2017 (domingo)", "9 de april de 2017 (sunday)"),
        ("día: 25 de febrero de 2019 (lunes)", "día: 25 de february de 2019 (monday)"),
    )

    @pytest.mark.parametrize("esp, eng", esp_eng)
    def test_english_to_spanish(self, esp, eng):
        assert Translator.english_to_spanish(eng) == esp

    @pytest.mark.parametrize("esp, eng", esp_eng)
    def test_spanish_to_english(self, esp, eng):
        assert Translator.spanish_to_english(esp) == eng


def test_gen_token():
    token = gen_token()
    assert len(token) == 12
    assert isinstance(token, str)
    assert token.isdigit()


@mock.patch("app.utils.request", autospec=True)
class TestGetPostArg:
    data_req_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "value"),
        ({"data": "  value  \n"}, "value"),
        ({"data": ""}, RuntimeError),
        ({"data": "  "}, RuntimeError),
        ({"data": " \n\n "}, RuntimeError),
        ({}, RuntimeError),
    )

    data_not_req_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "value"),
        ({"data": "  value  \n"}, "value"),
        ({"data": ""}, None),
        ({"data": "  "}, None),
        ({"data": " \n\n "}, None),
        ({}, None),
    )

    data_req_not_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "  value  "),
        ({"data": "  value  \n"}, "  value  \n"),
        ({"data": ""}, RuntimeError),
        ({"data": "  "}, "  "),
        ({"data": " \n\n "}, " \n\n "),
        ({}, RuntimeError),
    )

    data_not_req_not_strip = (
        ({"data": "value"}, "value"),
        ({"data": "  value  "}, "  value  "),
        ({"data": "  value  \n"}, "  value  \n"),
        ({"data": ""}, ""),
        ({"data": "  "}, "  "),
        ({"data": " \n\n "}, " \n\n "),
        ({}, None),
    )

    @pytest.mark.parametrize("request_data, expected", data_req_strip)
    def test_req_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        if expected == RuntimeError:
            with pytest.raises(expected):
                get_post_arg("data", required=True, strip=True)
        else:
            assert get_post_arg("data", required=True, strip=True) == expected

    @pytest.mark.parametrize("request_data, expected", data_not_req_strip)
    def test_not_req_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        assert get_post_arg("data", required=False, strip=True) == expected

    @pytest.mark.parametrize("request_data, expected", data_req_not_strip)
    def test_req_not_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        if expected == RuntimeError:
            with pytest.raises(expected):
                get_post_arg("data", required=True, strip=False)
        else:
            assert get_post_arg("data", required=True, strip=False) == expected

    @pytest.mark.parametrize("request_data, expected", data_not_req_not_strip)
    def test_not_req_not_strip(self, request_mock, request_data, expected):
        request_mock.form = request_data
        assert get_post_arg("data", required=False, strip=False) == expected