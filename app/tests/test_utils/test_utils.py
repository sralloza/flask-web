from pathlib import Path
from unittest import mock

import pytest
from requests.exceptions import ConnectionError

from app.utils import (
    PRINCIPAL_URL,
    Tokens,
    Translator,
    _Cache,
    get_last_menus_page,
    get_post_arg,
)


class TestGetLastMenusPage:
    url_expected = (
        "https://www.residenciasantiago.es/2019/06/20/del-21-al-24-de-junio-2019/"
    )
    warning_conn_error = (
        "Connection error downloading principal url (%r) (%d retries left)"
    )
    dmm_error = (
        "Could not retrieve url, trying to parse it by download principal url (%s)",
        PRINCIPAL_URL,
    )

    @pytest.fixture()
    def mocks(self):
        dmm_mock = mock.patch(
            "app.menus.core.daily_menus_manager.DailyMenusManager", autospec=True
        ).start()
        get_mock = mock.patch("requests.get", autospec=True).start()
        logger_mock = mock.patch("app.utils.logger", autospec=True).start()

        yield dmm_mock, get_mock, logger_mock

        mock.patch.stopall()

    @pytest.fixture(scope="class")
    def test_content(self):
        path = Path(__file__).parent.parent / "data" / "get_urls.txt"

        with path.open() as f:
            return f.read()

    def test_use_cache(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks
        _Cache.redirect_url = self.url_expected
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        get_mock.return_value = foo_mock
        url = get_last_menus_page()

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.debug.assert_any_call("Found in cache: %s", self.url_expected)
        assert url == self.url_expected

        assert logger_mock.debug.call_count == 2
        dmm_mock.assert_not_called()
        get_mock.assert_not_called()

    def test_from_dmm(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks

        _Cache.redirect_url = None
        get_mock.return_value.text = test_content
        menu_mock = mock.MagicMock()
        menu_mock.url = self.url_expected
        menu_mock.id = 1
        dmm_mock.return_value.__iter__.return_value = [menu_mock]

        url = get_last_menus_page()

        dmm_mock.return_value.load_from_database.assert_called_once_with()
        dmm_mock.return_value.sort.assert_called_once_with()

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.warning.assert_not_called()
        logger_mock.debug.assert_any_call(
            "Retrieving url from last menu (%d): %s", 1, self.url_expected
        )
        assert logger_mock.debug.call_count == 2

        assert url == self.url_expected
        assert self.url_expected == _Cache.redirect_url

    def test_with_request_no_connection_error(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks

        _Cache.redirect_url = None
        dmm_mock.return_value.__iter__.return_value = []
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        get_mock.return_value = foo_mock
        url = get_last_menus_page()

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.debug.assert_any_call("Set retries=%d", 5)
        logger_mock.warning.assert_any_call(*self.dmm_error)
        assert logger_mock.debug.call_count == 2

        dmm_mock.assert_called_once_with()

        assert url == self.url_expected

    def test_one_connection_error(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks

        _Cache.redirect_url = None
        dmm_mock.return_value.__iter__.return_value = []
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        get_mock.side_effect = iter([ConnectionError, foo_mock])

        url = get_last_menus_page()

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.debug.assert_any_call("Set retries=%d", 5)
        assert logger_mock.debug.call_count == 2

        logger_mock.warning.assert_any_call(*self.dmm_error)
        logger_mock.warning.assert_any_call(
            self.warning_conn_error, PRINCIPAL_URL, 4,
        )
        assert logger_mock.warning.call_count == 2

        dmm_mock.assert_called_once_with()
        assert url == self.url_expected

    def test_two_connection_error(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks

        _Cache.redirect_url = None
        dmm_mock.return_value.__iter__.return_value = []
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        get_mock.side_effect = iter([ConnectionError, ConnectionError, foo_mock])

        url = get_last_menus_page()

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.debug.assert_any_call("Set retries=%d", 5)
        assert logger_mock.debug.call_count == 2

        logger_mock.warning.assert_any_call(*self.dmm_error)
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 4),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 3),
            ]
        )
        assert logger_mock.warning.call_count == 3

        dmm_mock.assert_called_once_with()
        assert url == self.url_expected

    def test_three_connection_error(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks

        _Cache.redirect_url = None
        dmm_mock.return_value.__iter__.return_value = []
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        get_mock.side_effect = iter(
            [ConnectionError, ConnectionError, ConnectionError, foo_mock]
        )

        url = get_last_menus_page()

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.debug.assert_any_call("Set retries=%d", 5)
        assert logger_mock.debug.call_count == 2

        logger_mock.warning.assert_any_call(*self.dmm_error)
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 4),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 3),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 2),
            ]
        )
        assert logger_mock.warning.call_count == 4

        dmm_mock.assert_called_once_with()
        assert url == self.url_expected

    def test_four_connection_error(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks

        _Cache.redirect_url = None
        dmm_mock.return_value.__iter__.return_value = []
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        get_mock.side_effect = iter(
            [
                ConnectionError,
                ConnectionError,
                ConnectionError,
                ConnectionError,
                foo_mock,
            ]
        )

        url = get_last_menus_page()

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.debug.assert_any_call("Set retries=%d", 5)
        assert logger_mock.debug.call_count == 2

        logger_mock.warning.assert_any_call(*self.dmm_error)
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 4),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 3),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 2),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 1),
            ]
        )
        assert logger_mock.warning.call_count == 5

        dmm_mock.assert_called_once_with()
        assert url == self.url_expected

    def test_five_connection_error(self, mocks, test_content):
        dmm_mock, get_mock, logger_mock = mocks

        _Cache.redirect_url = None
        dmm_mock.return_value.__iter__.return_value = []
        foo_mock = mock.Mock()
        foo_mock.text = test_content
        get_mock.side_effect = iter(
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

        logger_mock.debug.assert_any_call("Getting last menus url")
        logger_mock.debug.assert_any_call("Set retries=%d", 5)
        assert logger_mock.debug.call_count == 2

        logger_mock.warning.assert_any_call(*self.dmm_error)
        logger_mock.warning.assert_has_calls(
            [
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 4),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 3),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 2),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 1),
                mock.call(self.warning_conn_error, PRINCIPAL_URL, 0),
            ]
        )
        assert logger_mock.warning.call_count == 6

        logger_mock.critical.assert_called_once_with(
            "Fatal connection error downloading principal url (%r) (%d retries)",
            PRINCIPAL_URL,
            5,
        )

        dmm_mock.assert_called_once_with()
        assert url == PRINCIPAL_URL


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


class TestTokens:
    check_token_data = (
        ("good", ["good", "yeah"], True),
        ("bad", ["good", "yeah"], False),
        ("bad", [], False),
        ("", [], False),
    )

    @pytest.mark.parametrize("token, tokens, result", check_token_data)
    @mock.patch("app.utils.Tokens.gen_tokens")
    def test_check_token(self, mock_gen_tokens, token, tokens, result):
        mock_gen_tokens.return_value = tokens
        real_result = Tokens.check_token(token)
        assert real_result == result

    def test_gen_primary_token(self):
        token = Tokens.gen_primary_token()
        assert len(token) == 12
        assert isinstance(token, str)
        assert token.isdigit()

    @mock.patch("app.utils.Tokens.get_tokens_from_file")
    @mock.patch("app.utils.Tokens.gen_primary_token")
    def test_gen_tokens(self, mock_gen_prim_token, mock_file_tokens):
        mock_gen_prim_token.return_value = "primary token"
        mock_file_tokens.return_value = "tokens from file".split()
        expected = ["primary token", "tokens", "from", "file"]
        real = Tokens.gen_tokens()

        assert real == expected

    test_get_tokens_from_file_data = (
        ("token1\ntoken2\ntoken3", ["token1", "token2", "token3"], False),
        ("\n\nt1\nt2", ["t1", "t2"], True),
        ("t1\n\n\nt2\nt3\n\nt4\n", ["t1", "t2", "t3", "t4"], True),
        ("\n\n\n\nt1\nt2\n\n\n\n", ["t1", "t2"], True),
        ("\n  \n  t1\n\tt2", ["t1", "t2"], True),
        ("    t1    \n    \tt2 \t  ", ["t1", "t2"], True),
    )

    @pytest.mark.parametrize(
        "file_text, tokens, update", test_get_tokens_from_file_data
    )
    @mock.patch("app.utils.Tokens.ensure_token_file_exists")
    @mock.patch("app.utils.Tokens.update_tokens_file")
    @mock.patch("app.utils.current_app")
    def test_get_tokens_from_file(
        self, app_mock, update_mock, ensure_mock, file_text, tokens, update
    ):
        m = mock.MagicMock()
        m.read_text.return_value = file_text

        def helper(_, item):
            if item == "TOKEN_FILE_PATH":
                return m
            raise KeyError

        app_mock.config.__getitem__ = helper

        result = Tokens.get_tokens_from_file()
        expected = tokens

        ensure_mock.assert_called_once_with()
        assert result == expected
        if update:
            update_mock.assert_called_once_with(tokens)
        else:
            update_mock.assert_not_called()

    @pytest.mark.parametrize("exists", [True, False])
    @mock.patch("app.utils.current_app")
    def test_ensure_token_file_exists(self, app_mock, exists):
        m = mock.MagicMock()
        m.exists.return_value = exists

        def helper(_, item):
            if item == "TOKEN_FILE_PATH":
                return m
            raise KeyError

        app_mock.config.__getitem__ = helper

        Tokens.ensure_token_file_exists()
        if exists:
            m.touch.assert_not_called()
        else:
            m.touch.assert_called_once_with()

    update_tokens_data = (
        (["t1"], "t1"),
        (["t1", "t2"], "t1\nt2"),
        (["t1", "t2", "t3"], "t1\nt2\nt3"),
        (["t1", "t2", "t3", "t4"], "t1\nt2\nt3\nt4"),
        (["t1", "t2", "t3", "t4", "t5"], "t1\nt2\nt3\nt4\nt5"),
        (["t1", "t2", "t3", "t4", "t5", "t6"], "t1\nt2\nt3\nt4\nt5\nt6"),
    )

    @pytest.mark.parametrize("tokens, text", update_tokens_data)
    @mock.patch("app.utils.current_app")
    def test_update_tokens_file(self, app_mock, tokens, text):
        m = mock.MagicMock()

        def helper(_, item):
            if item == "TOKEN_FILE_PATH":
                return m
            raise KeyError

        app_mock.config.__getitem__ = helper

        Tokens.update_tokens_file(tokens)
        m.write_text.assert_called_once_with(text)
