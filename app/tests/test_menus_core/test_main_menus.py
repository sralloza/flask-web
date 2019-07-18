from datetime import date

import pytest

from app.menus.core import DailyMenusManager, has_day, Patterns
from app.menus.core.structure import Meal, DailyMenu
from app.menus.models import DailyMenu as DailyMenuDB


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
    def test__contains__(self):
        pass

    @pytest.mark.skip
    def testsort(self):
        pass

    @pytest.mark.skip
    def testto_string(self):
        pass

    @pytest.mark.skip
    def testto_html(self):
        pass

    @pytest.mark.skip
    def testadd_to_menus(self):
        pass

    @pytest.mark.skip
    def testload(self):
        pass

    @pytest.mark.skip
    def testload_from_database(self):
        pass

    @pytest.mark.skip
    def testsave_to_database(self):
        pass

    @pytest.mark.skip
    def testload_from_menus_urls(self):
        pass

    @pytest.mark.skip
    def testprocess_url(self):
        pass

    @pytest.mark.skip
    def test_process_texts(self):
        pass

    @pytest.mark.skip
    def test_update_menu(self):
        pass


@pytest.mark.skip
class TestDailyMenusManagerOld:
    @pytest.fixture
    def dmm(self):
        dmm = DailyMenusManager()
        dm = DailyMenu

        dmm.menus = [
            dm(1, 9, 2019, lunch=Meal(), dinner=Meal()),
            dm(1, 8, 2019, lunch=Meal(), dinner=Meal(p1='D1')),
            dm(1, 7, 2019, lunch=Meal(), dinner=Meal(p1='D1', p2='D2')),
            dm(1, 6, 2019, lunch=Meal(p1='L1'), dinner=Meal()),
            dm(1, 5, 2019, lunch=Meal(p1='L1'), dinner=Meal(p1='D1')),
            dm(1, 4, 2019, lunch=Meal(p1='L1'), dinner=Meal(p1='D1', p2='D2')),
            dm(1, 3, 2019, lunch=Meal(p1='L1', p2='L2'), dinner=Meal()),
            dm(1, 2, 2019, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1')),
            dm(1, 1, 2019, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1', p2='D2')),
        ]
        return dmm

    def test_day_pattern(self):
        test = Patterns.day_pattern.search

        assert test('DÍA: 05 DE MARZO DE 2019 (MARTES)')
        assert test('DÍA: 05 DE JUNIO DE 2019 (MARTES)')
        assert not test('DÍA: 4 DE 2019 DE MARZO (MARTES')
        assert not test('day: 15 of 1562, june')
        assert not test('BUFFET: LECHE, CAFÉ, COLACAO, BIZCOCHO, GALLETAS, TOSTADAS, PAN,')
        assert test('DÍA: 06 DE MARZO DE 2019 (MIERCOLES)')
        assert not test('DÍA: 07 DE MARZO\nDE 2019 (JUEVES)')
        assert not test('1ER PLATO: ENSALADA TROPICAL')
        assert not test('CENA:\n\n\n \n\nCÓCTEL ESPAÑOL')
        assert test('DÍA: 11 DE MARZO DE 2019 (LUNES)')

    def test_fix_dates_pattern(self):
        test = Patterns.fix_dates_pattern_1.search

        assert test('febrero\n2010')
        assert test('word\n1000')
        assert not test('word_\n544')
        assert not test('dfsaf 5465')
        assert not test('word\n\n156')
        assert not test('156\nword')
        assert not test('dsafsfdsafsf')
        assert not test('\n\n\n\n\n')

    def test_ignore_patterns(self):
        def ignore(x):
            for pat in Patterns.ignore_patters:
                if pat.search(x) is not None:
                    return True
            return False

        assert ignore('2019. Febrero 20')
        assert ignore('semana del 20 al 30 de febrero')
        assert ignore('semana del 1 de enero al 15 de julio 2020')

    def test_contains(self, dmm: DailyMenusManager):
        assert date(2019, 1, 1) in dmm
        assert date(2019, 4, 1) in dmm
        assert date(2019, 5, 1) in dmm
        assert date(2019, 8, 1) in dmm
        assert date(2019, 9, 1) in dmm

        with pytest.raises(TypeError, match='Contains does only work with dates'):
            # noinspection PyTypeChecker
            assert 'anything' in dmm

    def test_sort(self, dmm: DailyMenusManager):
        ideal_dates = [x.date for x in dmm]
        ideal_dates.sort(reverse=True)
        dmm.sort()
        real_dates = [x.date for x in dmm]

        assert real_dates == ideal_dates

    def test_to_string(self, dmm: DailyMenusManager):
        string = dmm.to_string()

        assert len(string)
        assert string.count('\n') == 47
        assert string.count('(') == 9
        assert string.count(')') == 9
        assert string.count('(') == string.count(')')

        assert string.count('Comida') == 6
        assert string.count('L1') == 6
        assert string.count('L2') == 3
        assert string.count('Comida') == string.count('L1')

        assert string.count('Cena') == 6
        assert string.count('D1') == 6
        assert string.count('D2') == 3
        assert string.count('Cena') == string.count('D1')

    def test_to_html(self, dmm: DailyMenusManager):
        assert dmm.to_html() == dmm.to_string().replace('\n', '<br>')

    def test_add_to_menus(self):
        dmm = DailyMenusManager()
        dm = DailyMenu
        dmm.add_to_menus(
            dm(31, 12, 1999, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1', p2='D2'))
        )

        assert date(1999, 12, 31) in dmm

        dmm.add_to_menus([
            dm(31, 12, 2030, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1', p2='D2')),
            dm(31, 12, 2040, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1', p2='D2')),
            dm(31, 12, 2050, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1', p2='D2')),
        ])

        assert date(2030, 12, 31) in dmm
        assert date(2040, 12, 31) in dmm
        assert date(2050, 12, 31) in dmm

    def test_save_to_database(self, client, dmm: DailyMenusManager):
        dmm1 = dmm
        dmm1.save_to_database()

        dmm2 = DailyMenusManager()
        from_database = DailyMenuDB.query.all()
        from_database = [x.to_normal_daily_menu() for x in from_database]
        dmm2.add_to_menus(from_database)

        dmm1.sort()
        dmm2.sort()

        assert dmm1.menus == dmm2.menus

    def test_load_from_database(self, dmm):
        dmm1 = dmm

        dmm2 = DailyMenusManager()
        dmm2.load_from_database()

        dmm1.sort()
        dmm2.sort()

        assert dmm1.menus == dmm2.menus

    def test_process_url(self):
        url = 'https://www.residenciasantiago.es/2019/02/18/semana-del-19-al-25-de-febrero-2019/'
        dmm = DailyMenusManager()
        dmm.process_url(url)

        dmm.sort()

        assert date(2019, 2, 19) in dmm
        assert date(2019, 2, 20) in dmm
        assert date(2019, 2, 21) in dmm
        assert date(2019, 2, 22) in dmm
        assert date(2019, 2, 23) in dmm
        assert date(2019, 2, 24) in dmm
        assert date(2019, 2, 25) in dmm


@pytest.mark.skip(reason='old')
class TestGeneral:
    def test_patch(self):
        dmm = DailyMenusManager()
        dmm.process_url(
            'https://www.residenciasantiago.es/2019/04/01/semana-del-2-al-8-de-abril-2019/')

        assert date(2019, 4, 6) in dmm
        assert date(2019, 4, 7) in dmm
