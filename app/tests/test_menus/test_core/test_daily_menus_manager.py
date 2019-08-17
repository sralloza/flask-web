import random
from datetime import date, datetime
from unittest import mock

import pytest

from app.menus.core.daily_menus_manager import DailyMenusManager
from app.menus.core.structure import DailyMenu, Meal


class TestDailyMenusManager:
    @pytest.fixture
    def dmm(self):
        dmm = DailyMenusManager()
        lunch = Meal('L1', 'L2')
        dinner = Meal('D1', 'D2')
        for e in range(1, 13):
            menu = DailyMenu(e, e, 2019, lunch, dinner)
            dmm.menus.append(menu)

        return dmm

    # noinspection PyTypeChecker
    def test_contains(self, dmm):
        assert date(2019, 1, 1) in dmm
        assert date(2019, 2, 2) in dmm
        assert date(2019, 3, 3) in dmm
        assert date(2019, 4, 4) in dmm
        assert date(2019, 5, 5) in dmm
        assert date(2019, 6, 6) in dmm
        assert date(2019, 7, 7) in dmm
        assert date(2019, 8, 8) in dmm
        assert date(2019, 9, 9) in dmm
        assert date(2019, 10, 10) in dmm
        assert date(2019, 11, 11) in dmm
        assert date(2019, 12, 12) in dmm

        with pytest.raises(TypeError, match='Contains does only work with dates'):
            assert object in dmm
        with pytest.raises(TypeError, match='Contains does only work with dates'):
            assert 5 in dmm
        with pytest.raises(TypeError, match='Contains does only work with dates'):
            assert 7 + 1j in dmm
        with pytest.raises(TypeError, match='Contains does only work with dates'):
            assert 'error' in dmm

    def test_sort(self, dmm):
        random.shuffle(dmm.menus)

        ideal_dates = [x.date for x in dmm]
        ideal_dates.sort(reverse=True)
        dmm.sort()
        real_dates = [x.date for x in dmm]

        assert real_dates == ideal_dates

    def test_to_string(self, dmm):
        string1 = dmm.to_string()
        string2 = str(dmm)
        string3 = repr(dmm)

        assert string1 == string2 == string3

        assert len(string1)
        assert string1.count('\n') == 95
        assert string1.count('(') == 12
        assert string1.count(')') == 12
        assert string1.count('(') == string1.count(')')

        assert string1.count('Comida') == 12
        assert string1.count('L1') == 12
        assert string1.count('L2') == 12
        assert string1.count('Comida') == string1.count('L1')

        assert string1.count('Cena') == 12
        assert string1.count('D1') == 12
        assert string1.count('D2') == 12
        assert string1.count('Cena') == string1.count('D1')

    def test_to_html(self, dmm):
        string = dmm.to_html()

        assert len(string)
        assert string.count('<br>') == 95
        assert string.count('(') == 12
        assert string.count(')') == 12
        assert string.count('(') == string.count(')')

        assert string.count('Comida') == 12
        assert string.count('L1') == 12
        assert string.count('L2') == 12
        assert string.count('Comida') == string.count('L1')

        assert string.count('Cena') == 12
        assert string.count('D1') == 12
        assert string.count('D2') == 12
        assert string.count('Cena') == string.count('D1')

    class TestAddToMenus:
        def test_one_menu(self, dmm):
            menu = DailyMenu(6, 12, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            assert date(2019, 12, 6) not in dmm

            dmm.add_to_menus(menu)
            assert date(2019, 12, 6) in dmm

        def test_multiples_menus(self, dmm):
            menu1 = DailyMenu(6, 12, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            menu2 = DailyMenu(6, 11, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            menu3 = DailyMenu(6, 10, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))

            assert date(2019, 12, 6) not in dmm
            assert date(2019, 11, 6) not in dmm
            assert date(2019, 10, 6) not in dmm

            dmm.add_to_menus([menu1, menu2, menu3])
            assert date(2019, 12, 6) in dmm
            assert date(2019, 11, 6) in dmm
            assert date(2019, 10, 6) in dmm

    class TestLoad:
        @pytest.fixture
        def mocks(self):
            std_mock = mock.patch(
                'app.menus.core.daily_menus_manager.DailyMenusManager.save_to_database').start()
            lfmu_mock = mock.patch(
                'app.menus.core.daily_menus_manager.DailyMenusManager.load_from_menus_urls').start()
            contains_mock = mock.patch(
                'app.menus.core.daily_menus_manager.DailyMenusManager.__contains__').start()
            lfd_mock = mock.patch(
                'app.menus.core.daily_menus_manager.DailyMenusManager.load_from_database').start()

            yield std_mock, lfmu_mock, contains_mock, lfd_mock

            mock.patch.stopall()

        def test_today_not_found_without_force(self, mocks):
            std_mock, lfmu_mock, contains_mock, lfd_mock = mocks
            contains_mock.return_value = False

            DailyMenusManager.load()

            contains_mock.assert_called_with(datetime.today().date())
            lfd_mock.assert_called_with()
            lfmu_mock.assert_called_with()
            std_mock.assert_called_with()

        def test_today_found_without_force(self, mocks):
            std_mock, lfmu_mock, contains_mock, lfd_mock = mocks
            contains_mock.return_value = True

            DailyMenusManager.load()

            contains_mock.assert_called_with(datetime.today().date())
            lfd_mock.assert_called_with()
            lfmu_mock.assert_not_called()
            std_mock.assert_not_called()

        def test_today_not_found_with_force(self, mocks):
            std_mock, lfmu_mock, contains_mock, lfd_mock = mocks
            contains_mock.return_value = False

            DailyMenusManager.load(force=True)

            contains_mock.assert_called_with(datetime.today().date())
            lfd_mock.assert_called_with()
            lfmu_mock.assert_called_with()
            std_mock.assert_called_with()

        def test_today_found_with_force(self, mocks):
            std_mock, lfmu_mock, contains_mock, lfd_mock = mocks
            contains_mock.return_value = True

            DailyMenusManager.load(force=True)

            contains_mock.assert_called_with(datetime.today().date())
            lfd_mock.assert_called_with()
            lfmu_mock.assert_called_with()
            std_mock.assert_called_with()

    def test_to_json(self):
        dmm = DailyMenusManager()
        menu1 = DailyMenu(6, 12, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
        menu2 = DailyMenu(6, 11, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))

        dmm.add_to_menus([menu1, menu2])

        expected_json = [
            {"id": 20191206, "day": 'Viernes 6', "lunch": {"p1": 'L1', "p2": 'L2'},
             "dinner": {"p1": 'D1', "p2": 'D2'}},
            {"id": 20191106, "day": 'Miércoles 6', "lunch": {"p1": 'L1', "p2": 'L2'},
             "dinner": {"p1": 'D1', "p2": 'D2'}}
        ]

        real_json = dmm.to_json()
        assert real_json == expected_json

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
