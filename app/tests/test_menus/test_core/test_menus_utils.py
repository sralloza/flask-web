from pathlib import Path
from typing import List, Tuple
from unittest import mock

import pytest
from flask import current_app
from requests.exceptions import ConnectionError

from app.config import Config
from app.menus.core.utils import (
    PRINCIPAL_URL,
    Patterns,
    filter_data,
    get_menus_urls,
    has_day,
)

from app.tests.data.data import FilterDataPaths




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

    @pytest.fixture(scope="class")
    def test_content(self):
        path = Path(__file__).parent.parent.parent / "data" / "get_urls.txt"

        with path.open() as f:
            return f.read()



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
