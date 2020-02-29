import json
from pathlib import Path
from unittest import mock

import pytest

from app.menus.core.utils import (
    PRINCIPAL_URL,
    TEMPLATE,
    Patterns,
    _Cache,
    filter_data,
    get_last_menus_url,
    get_menus_urls,
    has_day,
)
from app.tests.data.data import FilterDataPaths
from app.tests.data.data import GetMenusUrlsDataPaths as GMUDP
from app.utils.exceptions import DownloaderError

gmu_test_data = []
ids = []
for input_path, output_path in zip(GMUDP.inputs.value, GMUDP.outputs.value):
    assert input_path.stem.replace(".html", "") == output_path.stem
    gmu_test_data.append(
        (
            input_path.read_text(encoding="utf-8"),
            output_path.read_text(encoding="utf-8"),
        )
    )
    ids.append(output_path.stem)


@mock.patch("requests.get", autospec=True)
@mock.patch("app.menus.core.utils.logger", autospec=True)
class TestGetMenusUrls:
    urls_expected = [
        "https://www.residenciasantiago.es/2019/06/20/del-21-al-24-de-junio-2019/",
        "https://www.residenciasantiago.es/2019/06/17/del-18-al-20-de-junio-2019/",
    ]

    warning_expected = (
        "Connection error downloading principal url (%r) (%d retries left)"
    )

    @pytest.fixture(autouse=True, scope="class")
    def autouse_client(self, client):
        # client must be used always becaulse get_menus_urls uses flask's config.
        return

    @pytest.mark.parametrize("input_data, output_data", gmu_test_data, ids=ids)
    def test_content(self, logger_mock, get_mock, input_data, output_data):
        expected = json.loads(output_data)
        interface = mock.MagicMock()
        interface.text = input_data
        get_mock.return_value = interface

        real = get_menus_urls(request_all=False)

        get_mock.assert_called_once_with(TEMPLATE % 1)
        assert real == expected


@pytest.mark.xfail
class TestGetLastMenusUrl:
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
        get_mock = mock.patch(
            "app.menus.core.utils.downloader.get", autospec=True
        ).start()
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
        url = get_last_menus_url()

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

        url = get_last_menus_url()

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
        url = get_last_menus_url()

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
        get_mock.side_effect = iter([DownloaderError, foo_mock])

        url = get_last_menus_url()

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
        get_mock.side_effect = iter([DownloaderError, DownloaderError, foo_mock])

        url = get_last_menus_url()

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
            [DownloaderError, DownloaderError, DownloaderError, foo_mock]
        )

        url = get_last_menus_url()

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
                DownloaderError,
                DownloaderError,
                DownloaderError,
                DownloaderError,
                foo_mock,
            ]
        )

        url = get_last_menus_url()

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
                DownloaderError,
                DownloaderError,
                DownloaderError,
                DownloaderError,
                DownloaderError,
                foo_mock,
            ]
        )

        url = get_last_menus_url()

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


class TestHasDay:
    data = (
        ("Día: 25 de diciembre de 2017 (martes)", True),
        ("Día: 07 de enero de 2019 (viernes)", True),
        ("Día: 1 de junio de 2000 (sábado)", True),
        ("Día:    1 de junio de 2000 (sábado)", True),
        ("Día: 1    de junio de 2000 (sábado)", True),
        ("Día: 1 de    junio de 2000 (sábado)", True),
        ("Día: 1 de junio    de 2000 (sábado)", True),
        ("Día: 1 de junio de    2000 (sábado)", True),
        ("Día: 1 de junio de 2000    (sábado)", True),
        ("Día: 1  de  junio  de 2000 (sábado)", True),
        ("Día: 1 de junio  de  2000  (sábado)", True),
        ("Día   : 1 de junio de 2000 (sábado)", True),
        ("Día: 1 de enero de 0001 (lunes)", True),
        ("Día: 1 de enero de 1 (lunes)", False),
        ("1 de enero de 1998 (jueves)", False),
        ("1 de marzo de 1930", False),
    )

    @pytest.mark.parametrize("day_str, result", data)
    def test_has_day(self, day_str, result):
        assert has_day(day_str) == result


class TestFilterData:
    def test_argument_type(self):
        assert filter_data("hola\nadios") == ""
        assert filter_data(["hola", "adios"]) == []

        with pytest.raises(TypeError, match="data must be str or list, not"):
            filter_data(1)
        with pytest.raises(TypeError, match="data must be str or list, not"):
            filter_data(2 + 3j)
        with pytest.raises(TypeError, match="data must be str or list, not"):
            filter_data(True)
        with pytest.raises(TypeError, match="data must be str or list, not"):
            filter_data(object)

    def test_separate_date(self):
        input_data = ["Día: 23 de diciembre", "de 2018 (martes)"]
        expected = ["día: 23 de diciembre de 2018 (martes)"]
        real = filter_data(input_data)

        assert real == expected

    def test_combined_easy(self):
        input_data = ["1er plato: combinado: jamón y queso"]
        expected = ["combinado: jamón y queso"]
        real = filter_data(input_data)

        assert real == expected

    def test_combined_split(self):
        input_data = ["1er plato: combinado: jamón", "y queso"]
        expected = ["combinado: jamón y queso"]
        real = filter_data(input_data)

        assert real == expected

    def test_combined_with_second(self):
        input_data = ["1er plato: combinado: jamón", "2 plato: y queso"]
        expected = ["combinado: jamón y queso"]
        real = filter_data(input_data)

        assert real == expected

    filter_data_paths = zip(FilterDataPaths.inputs.value, FilterDataPaths.outputs.value)

    @pytest.mark.parametrize("input_path, output_path", filter_data_paths)
    def test_all(self, input_path, output_path):
        input_data = input_path.read_text(encoding="utf-8").splitlines()
        output_data = output_path.read_text(encoding="utf-8").splitlines()
        real = filter_data(input_data)

        assert real == output_data


class TestPatterns:
    day_pattern_data = (
        ("día: 23 de diciembre de 1998 (martes)", True),
        ("día: 29 de junio de 1023 (jueves)", True),
        ("día: 00 de enero de 0000 (lunes)", True),
        ("día: 05 de marzo de 2019 (martes)", True),
        ("día: 06 de junio de 2019 (martes)", True),
        ("día: 04 de 2019 de marzo (martes", False),
        ("día: 4 de 2019 de marzo (martes", False),
        ("día:04 de marzo de 2019 (martes)", True),
        ("día:04demarzode2019(martes)", True),
        ("day: 15 of 1562, june", False),
        ("buffet: leche, café, colacao, bizcocho, galletas, tostadas, pan,", False),
        ("día: 06 de marzo de 2019 (miercoles)", True),
        ("día: 07 de marzo\nde 2019 (jueves)", True),
        ("1er plato: ensalada tropical", False),
        ("cena:\n\n\n \n\ncóctel español", False),
        ("día: 11 de marzo de 2019 (lunes)", True),
    )

    @pytest.mark.parametrize("string, match_code", day_pattern_data)
    def test_day_pattern(self, string, match_code):
        pattern_match = Patterns.day_pattern.search(string)

        if match_code:
            assert pattern_match is not None
            assert pattern_match.group() == string
        else:
            assert pattern_match is None

    semi_day_pattern_1_data = (
        ("día: 25 de diciembre", True),
        ("día: 01 de febrero", True),
        ("Día: 31 de octubre", True),
        ("Día:    12   \t  de    octubre", True),
        ("Día:\t1\tde\tagosto", True),
        ("día:12deoctubre", True),
        ("cena: cóctel español", False),
    )

    @pytest.mark.parametrize("string, match_code", semi_day_pattern_1_data)
    def test_semi_day_pattern_1(self, string, match_code):
        pattern_match = Patterns.semi_day_pattern_1.search(string)

        if match_code:
            assert pattern_match is not None
            assert pattern_match.group() == string
        else:
            assert pattern_match is None

    semi_day_pattern_2_data = (
        ("2019 (martes)", True),
        ("2019 (  martes  )", True),
        ("2019(martes)", True),
        ("2019\t\t(martes)", True),
        ("2019    (martes)", True),
        ("2019    (  martes  )", True),
        ("cóctel", False),
    )

    @pytest.mark.parametrize("string, match_code", semi_day_pattern_2_data)
    def test_semi_day_pattern_2(self, string, match_code):
        pattern_match = Patterns.semi_day_pattern_2.search(string)

        if match_code:
            assert pattern_match is not None
            assert pattern_match.group() == string
        else:
            assert pattern_match is None

    fix_dates_patterns_1_data = (
        ("febrero\n2019", "febrero 2019"),
        ("febrero \n 2019", "febrero 2019"),
        ("febrero2019", "febrero 2019"),
        ("febrerode\n201", None),
    )

    @pytest.mark.parametrize("string, expected_sub", fix_dates_patterns_1_data)
    def test_fix_dates_pattern_1(self, string, expected_sub):
        real_sub = Patterns.fix_dates_pattern_1.sub(r"\1 \2", string)
        pattern_match = Patterns.fix_dates_pattern_1.search(string)

        if expected_sub:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None

    fix_dates_patterns_2_data = (
        ("día:     20", "día: 20"),
        ("día:  \t\t20", "día: 20"),
        ("día:20", "día: 20"),
        ("día:\n\t\n\t20", "día: 20"),
        ("day: 20", None),
    )

    @pytest.mark.parametrize("string, expected_sub", fix_dates_patterns_2_data)
    def test_fix_dates_pattern_2(self, string, expected_sub):
        real_sub = Patterns.fix_dates_pattern_2.sub(r"\1 \2", string)
        pattern_match = Patterns.fix_dates_pattern_2.search(string)

        if expected_sub:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None

    fix_dates_patterns_3_data = (
        ("día: 27 de enero de 2020 (sábado)", None),
        ("día: 25 de abril de 2020 (viernes", "día: 25 de abril de 2020 (viernes)"),
    )

    @pytest.mark.parametrize("string, expected_sub", fix_dates_patterns_3_data)
    def test_fix_dates_pattern_3(self, string, expected_sub):
        real_sub = Patterns.fix_dates_pattern_3.sub(r"\1)", string)
        pattern_match = Patterns.fix_dates_pattern_3.search(string)

        if expected_sub:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None

    fix_content_pattern_1 = (
        ("cocido\ncompleto", "cocido completo"),
        ("fruta\ndía:", None),
    )

    @pytest.mark.parametrize("string, expected_sub", fix_content_pattern_1)
    def test_fix_content_pattern_1(self, string, expected_sub):
        real_sub = Patterns.fix_content_pattern_1.sub(r"\1 \2", string)
        pattern_match = Patterns.fix_content_pattern_1.search(string)

        if expected_sub:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None

    fix_content_pattern_2 = (
        ("    ", " "),
        ("\t \t\t \t", " "),
        ("\t", None),
        ("\t\t", " "),
        ("hola que tal estás", None),
    )

    @pytest.mark.parametrize("string, expected_sub", fix_content_pattern_2)
    def test_fix_content_pattern_2(self, string, expected_sub):
        real_sub = Patterns.fix_content_pattern_2.sub(r" ", string)
        pattern_match = Patterns.fix_content_pattern_2.search(string)

        if expected_sub:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None

    fix_content_pattern_3 = (
        ("1er plato: sardinas postre: manzana", "1er plato: sardinas\npostre: manzana"),
        ("el postre será barato", None),
    )

    @pytest.mark.parametrize("string, expected_sub", fix_content_pattern_3)
    def test_fix_content_pattern_3(self, string, expected_sub):
        real_sub = Patterns.fix_content_pattern_3.sub(r"\1\n\2", string)
        pattern_match = Patterns.fix_content_pattern_3.search(string)

        if expected_sub:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None
