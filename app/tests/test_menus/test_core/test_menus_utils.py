from pathlib import Path
from typing import Tuple, List
from unittest import mock

import pytest
from requests.exceptions import ConnectionError

from app.config import Config
from app.menus.core.utils import get_menus_urls, PRINCIPAL_URL, has_day, filter_data, \
    Patterns

_inputs = Path(Config.TEST_DATA_PATH / 'filter_data' / 'input').glob('*.txt')
_outputs = Path(Config.TEST_DATA_PATH / 'filter_data' / 'output').glob('*.txt')

metadata_type = List[Tuple[Path, Path]]

metadata_paths: metadata_type = []

for _input_path in _inputs:
    for _output_path in _outputs:
        if _input_path.stem == _output_path.stem:
            metadata_paths.append((_input_path, _output_path))
            break


@mock.patch('requests.get')
@mock.patch('app.menus.core.utils.logger')
class TestGetMenusUrls:
    urls_expected = ['https://www.residenciasantiago.es/2019/06/20/del-21-al-24-de-junio-2019/',
                     'https://www.residenciasantiago.es/2019/06/17/del-18-al-20-de-junio-2019/']

    warning_expected = 'Connection error downloading principal url (%r) (%d retries left)'

    @pytest.fixture(scope='class')
    def test_content(self):
        path = Path(__file__).parent.parent.parent / 'data' / 'get_urls.txt'

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


class TestHasDay:
    data = (
        ('Día: 25 de diciembre de 2017 (martes)', True),
        ('Día: 07 de enero de 2019 (viernes)', True),
        ('Día: 1 de junio de 2000 (sábado)', True),
        ('Día:    1 de junio de 2000 (sábado)', True),
        ('Día: 1    de junio de 2000 (sábado)', True),
        ('Día: 1 de    junio de 2000 (sábado)', True),
        ('Día: 1 de junio    de 2000 (sábado)', True),
        ('Día: 1 de junio de    2000 (sábado)', True),
        ('Día: 1 de junio de 2000    (sábado)', True),
        ('Día: 1  de  junio  de 2000 (sábado)', True),
        ('Día: 1 de junio  de  2000  (sábado)', True),
        ('Día   : 1 de junio de 2000 (sábado)', True),
        ('Día: 1 de enero de 0001 (lunes)', True),
        ('Día: 1 de enero de 1 (lunes)', False),
        ('1 de enero de 1998 (jueves)', False),
        ('1 de marzo de 1930', False),
    )

    @pytest.mark.parametrize('day_str, result', data)
    def test_has_day(self, day_str, result):
        assert has_day(day_str) == result


class TestFilterData:
    # noinspection PyTypeChecker
    def test_argument_type(self):
        assert filter_data('hola\nadios') == ''
        assert filter_data(['hola', 'adios']) == []

        with pytest.raises(TypeError, match='data must be str or list, not'):
            filter_data(1)
        with pytest.raises(TypeError, match='data must be str or list, not'):
            filter_data(2 + 3j)
        with pytest.raises(TypeError, match='data must be str or list, not'):
            filter_data(True)
        with pytest.raises(TypeError, match='data must be str or list, not'):
            filter_data(object)

    def test_normal(self):
        input_data = ['1er plato:  ', '   1 plato:   ', '2º plato:   ', '2o plato:', '2 plato:',
                      'desayuno', 'CoMiDa  ', 'cena', 'combinado', 'cóctel', 'coctel', '', '', '',
                      '', 'día: 29 de febrero de 2019 (viernes)']
        expected = ['1er plato:', '1er plato:', '2º plato:', '2º plato:', '2º plato:', 'comida',
                    'cena', 'combinado', 'cóctel', 'cóctel', 'día: 29 de febrero de 2019 (viernes)']
        real = filter_data(input_data)

        assert real == expected

    def test_separate_date(self):
        input_data = ['Día: 23 de diciembre', 'de 2018 (martes)']
        expected = ['día: 23 de diciembre de 2018 (martes)']
        real = filter_data(input_data)

        assert real == expected

    def test_combined_easy(self):
        input_data = ['1er plato: combinado: jamón y queso']
        expected = ['combinado: jamón y queso']
        real = filter_data(input_data)

        assert real == expected

    def test_combined_split(self):
        input_data = ['1er plato: combinado: jamón', 'y queso']
        expected = ['combinado: jamón y queso']
        real = filter_data(input_data)

        assert real == expected

    def test_combined_with_second(self):
        input_data = ['1er plato: combinado: jamón', '2 plato: y queso']
        expected = ['combinado: jamón y queso']
        real = filter_data(input_data)

        assert real == expected

    @pytest.mark.parametrize('input_path, output_path', metadata_paths)
    def test_meta(self, input_path, output_path):
        with input_path.open(encoding='utf-8') as fh:
            input_data = fh.read().splitlines()

        with output_path.open(encoding='utf-8') as fh:
            output_data = fh.read().splitlines()

        real_data = filter_data(input_data)

        assert output_data == real_data


class TestPatterns:
    day_pattern_data = (
        ('día: 23 de diciembre de 1998 (martes)', True),
        ('día: 29 de junio de 1023 (jueves)', True),
        ('día: 00 de enero de 0000 (lunes)', True),
        ('día: 05 de marzo de 2019 (martes)', True),
        ('día: 06 de junio de 2019 (martes)', True),
        ('día: 04 de 2019 de marzo (martes', False),
        ('día: 4 de 2019 de marzo (martes', False),
        ('día:04 de marzo de 2019 (martes)', True),
        ('día:04demarzode2019(martes)', True),
        ('day: 15 of 1562, june', False),
        ('buffet: leche, café, colacao, bizcocho, galletas, tostadas, pan,', False),
        ('día: 06 de marzo de 2019 (miercoles)', True),
        ('día: 07 de marzo\nde 2019 (jueves)', True),
        ('1er plato: ensalada tropical', False),
        ('cena:\n\n\n \n\ncóctel español', False),
        ('día: 11 de marzo de 2019 (lunes)', True),
    )

    @pytest.mark.parametrize('string, match_code', day_pattern_data)
    def test_day_pattern(self, string, match_code):
        pattern_match = Patterns.day_pattern.search(string)

        if match_code:
            assert pattern_match is not None
            assert pattern_match.group() == string
        else:
            assert pattern_match is None

    semi_day_pattern_1_data = (
        ('día: 25 de diciembre', True),
        ('día: 01 de febrero', True),
        ('Día: 31 de octubre', True),
        ('Día:    12   \t  de    octubre', True),
        ('Día:\t1\tde\tagosto', True),
        ('día:12deoctubre', True),
        ('cena: cóctel español', False)
    )

    @pytest.mark.parametrize('string, match_code', semi_day_pattern_1_data)
    def test_semi_day_pattern_1(self, string, match_code):
        pattern_match = Patterns.semi_day_pattern_1.search(string)

        if match_code:
            assert pattern_match is not None
            assert pattern_match.group() == string
        else:
            assert pattern_match is None

    semi_day_pattern_2_data = (
        ('2019 (martes)', True),
        ('2019 (  martes  )', True),
        ('2019(martes)', True),
        ('2019\t\t(martes)', True),
        ('2019    (martes)', True),
        ('2019    (  martes  )', True),
        ('cóctel', False)
    )

    @pytest.mark.parametrize('string, match_code', semi_day_pattern_2_data)
    def test_semi_day_pattern_2(self, string, match_code):
        pattern_match = Patterns.semi_day_pattern_2.search(string)

        if match_code:
            assert pattern_match is not None
            assert pattern_match.group() == string
        else:
            assert pattern_match is None

    fix_dates_patterns_1_data = (
        ('febrero\n2019', True, 'febrero 2019'),
        ('febrero \n 2019', True, 'febrero 2019'),
        ('febrero2019', True, 'febrero 2019'),
        ('febrerode\n201', False, None),
    )

    @pytest.mark.parametrize('string, match_code, expected_sub', fix_dates_patterns_1_data)
    def test_fix_dates_pattern_1(self, string, match_code, expected_sub):
        real_sub = Patterns.fix_dates_pattern_1.sub(r'\1 \2', string)
        pattern_match = Patterns.fix_dates_pattern_1.search(string)

        if match_code:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None

    fix_dates_patterns_2_data = (
        ('día:     20', True, 'día: 20'),
        ('día:  \t\t20', True, 'día: 20'),
        ('día:20', True, 'día: 20'),
        ('día:\n\t\n\t20', True, 'día: 20'),
        ('day: 20', False, None)
    )

    @pytest.mark.parametrize('string, match_code, expected_sub', fix_dates_patterns_2_data)
    def test_fix_dates_pattern_2(self, string, match_code, expected_sub):
        real_sub = Patterns.fix_dates_pattern_2.sub(r'\1 \2', string)
        pattern_match = Patterns.fix_dates_pattern_2.search(string)

        if match_code:
            assert pattern_match is not None
            assert real_sub == expected_sub
        else:
            assert pattern_match is None

    ignore_patterns_data = (
        ('20. septiembre 2019', True),
        ('02. septiembre 2019', True),
        ('2. septiembre 2019', True),
        ('semana del 20 al 29 de junio', True),
        ('semana del 2 al 2 de junio', True),
        ('semana del 02 al 02 de junio', True),
        ('semana del 20 de mayo al 20 de junio 2019', True),
        ('semana del 02 de mayo al 02 de junio 2019', True),
        ('semana del 2 de mayo al 2 de junio 2019', True),
        ('desayuno: bacalao con tomate', False),
        ('comida: patatas con patatas', False)
    )

    @pytest.mark.parametrize('string, match_code', ignore_patterns_data)
    def test_ignore_patterns(self, string, match_code):
        def match(any_string):
            for pattern in Patterns.ignore_patters:
                if pattern.search(any_string) is not None:
                    return True
            return False

        pattern_match = match(string)
        if match_code:
            assert pattern_match is True
        else:
            assert pattern_match is False
