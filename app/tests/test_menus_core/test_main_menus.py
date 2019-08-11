from unittest import mock

import pytest

from app.menus.core.utils import has_day, Worker


@pytest.mark.skip(reason='old')
class TestFunctions:
    has_day_args = [
        ('DÍA: 05 DE MARZO DE 2019 (MARTES)', 1),
        ('DÍA: 05 DE JUNIO DE 2019 (MARTES)', 1),
        ('DÍA: 4 DE 2019 DE MARZO (MARTES', 0),
        ('day: 15 of 1562, june', 0),
        ('BUFFET: LECHE, CAFÉ, COLACAO, BIZCOCHO, GALLETAS, TOSTADAS, PAN,', 0),
        ('DÍA: 06 DE MARZO DE 2019 (MIERCOLES)', 1),
        ('DÍA: 07 DE MARZO\nDE 2019 (JUEVES)', 0),
        ('1ER PLATO: ENSALADA TROPICAL', 0),
        ('CENA:\n\n\n \n\nCÓCTEL ESPAÑOL', 0),
        ('DÍA: 11 DE MARZO DE 2019 (LUNES)', 1),
    ]

    @pytest.mark.parametrize('str_to_parse, parse_code', has_day_args)
    def test_has_day(self, str_to_parse, parse_code):
        if parse_code == 1:
            assert has_day(str_to_parse)
        elif parse_code == 0:
            assert not has_day(str_to_parse)
        else:
            assert 0, 'Invalid parse code'

    @pytest.mark.skip
    def test_filer_data(self):
        pass


class TestPatterns:
    @pytest.mark.skip
    def test_day_pattern(self):
        pass

    @pytest.mark.skip
    def test_semi_day_pattern_1(self):
        pass

    @pytest.mark.skip
    def test_semi_day_pattern_2(self):
        pass

    @pytest.mark.skip
    def test_fix_dates_pattern_1(self):
        pass

    @pytest.mark.skip
    def test_fix_dates_pattern_2(self):
        pass

    @pytest.mark.skip
    def test_ignore_patters(self):
        pass


class TestDailyMenusManager:
    @pytest.mark.skip
    def test_contains(self):
        pass

    @pytest.mark.skip
    def test_sort(self):
        pass

    @pytest.mark.skip
    def test_to_string(self):
        pass

    @pytest.mark.skip
    def test_to_html(self):
        pass

    @pytest.mark.skip
    def test_add_to_menus(self):
        pass

    @pytest.mark.skip
    def test_load(self):
        pass

    @pytest.mark.skip
    def test_load_from_database(self):
        pass

    @pytest.mark.skip
    def test_save_to_database(self):
        pass

    @pytest.mark.skip
    def test_load_from_menus_urls(self):
        pass

    @pytest.mark.skip
    def test_process_url(self):
        pass

    @pytest.mark.skip
    def test_process_texts(self):
        pass

    @pytest.mark.skip
    def test_update_menu(self):
        pass


class TestWorker:
    @mock.patch('app.menus.core.logger.debug', spec=True)
    def test_run(self, logger_mock):
        m = mock.Mock()
        w = Worker('http://example.com', m)

        w.run()

        logger_mock.assert_called_once_with('Starting worker with url %s', 'http://example.com')
        m.process_url.assert_called_once_with('http://example.com', 5)

