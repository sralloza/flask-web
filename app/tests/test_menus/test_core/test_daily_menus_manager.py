import random
from datetime import date, datetime
from unittest import mock

import pytest

from app.menus.core.daily_menus_manager import DailyMenusManager
from app.menus.core.structure import DailyMenu, Meal
from app.menus.models import DailyMenuDB


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
        def test_one_menu(self):
            dmm = DailyMenusManager()

            menu = DailyMenu(6, 12, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            assert date(2019, 12, 6) not in dmm

            dmm.add_to_menus(menu)
            assert date(2019, 12, 6) in dmm

        def test_multiples_menus(self):
            dmm = DailyMenusManager()

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

        def test_multiple_calls(self):
            dmm = DailyMenusManager()

            menu1 = DailyMenu(6, 12, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            menu2 = DailyMenu(6, 11, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            menu3 = DailyMenu(6, 10, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))

            assert len(dmm) == 0
            assert date(2019, 12, 6) not in dmm
            assert date(2019, 11, 6) not in dmm
            assert date(2019, 10, 6) not in dmm

            dmm.add_to_menus(menu1)
            assert len(dmm) == 1
            assert date(2019, 12, 6) in dmm
            assert date(2019, 11, 6) not in dmm
            assert date(2019, 10, 6) not in dmm

            dmm.add_to_menus(menu2)
            assert len(dmm) == 2
            assert date(2019, 12, 6) in dmm
            assert date(2019, 11, 6) in dmm
            assert date(2019, 10, 6) not in dmm

            dmm.add_to_menus(menu3)
            assert len(dmm) == 3
            assert date(2019, 12, 6) in dmm
            assert date(2019, 11, 6) in dmm
            assert date(2019, 10, 6) in dmm

        def test_add_duplicate_menus(self):
            dmm = DailyMenusManager()

            menu1 = DailyMenu(6, 12, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            menu2 = DailyMenu(6, 11, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))
            menu3 = DailyMenu(6, 10, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))

            assert len(dmm) == 0
            assert date(2019, 12, 6) not in dmm
            assert date(2019, 11, 6) not in dmm
            assert date(2019, 10, 6) not in dmm

            dmm.add_to_menus([menu1, menu2, menu3])
            assert len(dmm) == 3
            assert date(2019, 12, 6) in dmm
            assert date(2019, 11, 6) in dmm
            assert date(2019, 10, 6) in dmm

            dmm.add_to_menus([menu1, menu2, menu3])
            assert len(dmm) == 3
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

    @mock.patch('app.menus.core.daily_menus_manager.DailyMenusManager.save_to_database')
    @mock.patch('app.menus.core.daily_menus_manager.DailyMenusManager.add_to_menus')
    @mock.patch('app.menus.core.daily_menus_manager.DailyMenusManager._add_manual')
    def test_add_manual(self, am_mock, atm_mock, std_mock):
        DailyMenusManager.add_manual()
        am_mock.assert_called_once()
        atm_mock.assert_called_once()
        std_mock.assert_called_once()

    @pytest.fixture
    def hidden_add_manual_mocks(self):
        input_mock = mock.patch('app.menus.core.daily_menus_manager.input').start()
        print_mock = mock.patch('app.menus.core.daily_menus_manager.print').start()
        confirm_mock = mock.patch(
            'app.menus.core.daily_menus_manager.DailyMenusManager._confirm').start()

        yield input_mock, print_mock, confirm_mock

        mock.patch.stopall()

    HIDDEN_ADD_MANUAL_GOOD = [1, 1, 2019, 'L1', 'L2', 'D1', 'D2']
    hidden_add_manual_data = (
        (HIDDEN_ADD_MANUAL_GOOD, True),
        (['X', 1, 2019, 'L1', 'L2', 'D1', 'D2'],
         "ValueError: invalid literal for int() with base 10: 'X'"),
        ([1, 'Y', 2019, 'L1', 'L2', 'D1', 'D2'],
         "ValueError: invalid literal for int() with base 10: 'Y'"),
        ([1, 1, 'Z', 'L1', 'L2', 'D1', 'D2'],
         "ValueError: invalid literal for int() with base 10: 'Z'"),
    )

    @pytest.mark.parametrize('input_side_effect, code', hidden_add_manual_data)
    def test_hidden_add_manual(self, input_side_effect, code, hidden_add_manual_mocks):
        input_mock, print_mock, confirm_mock = hidden_add_manual_mocks
        all_right = code is True

        if not all_right:
            input_mock.side_effect = input_side_effect + self.HIDDEN_ADD_MANUAL_GOOD
        else:
            input_mock.side_effect = input_side_effect

        menu = DailyMenusManager._add_manual()

        assert isinstance(menu, DailyMenu)
        input_mock.assert_called()

        print_mock.has_call('Saving...')

        if not all_right:
            print_mock.has_call(code)

    data = (
        ('no', False), ('si', True), ('sí', True), ('Yes', True), ('No', False), ('Si', True),
        ('Sí', True), ('other', -1), ('0', False), ('1', True), ('asdfsadf', -1), ('quit', -2)
    )

    @pytest.mark.parametrize('arg, expect', data)
    @mock.patch('app.menus.core.daily_menus_manager.input')
    @mock.patch('app.menus.core.daily_menus_manager.print')
    def test_confirm(self, print_mock, input_mock, arg, expect):
        if expect == -1:
            input_mock.side_effect = (arg, 'Y')
        else:
            input_mock.return_value = arg

        if expect == -2:
            with pytest.raises(SystemExit):
                DailyMenusManager._confirm('Whatever')
            print_mock.assert_called_with('Cancelled')
            return

        got = DailyMenusManager._confirm('Whatever')

        if expect == -1:
            print_mock.assert_called_with('Invalid response')
            input_mock.assert_called_with('Whatever [y/n/q]\t')
            assert input_mock.call_count == 2
        else:
            print_mock.assert_not_called()
            input_mock.assert_called_once_with('Whatever [y/n/q]\t')
            assert got == expect

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

    @mock.patch('app.menus.core.daily_menus_manager.DailyMenuDB')
    @mock.patch('app.menus.core.daily_menus_manager.DailyMenusManager.add_to_menus')
    def test_load_from_database(self, atm_mock, dmdb_mock):
        dmdb_mock.query.all.return_value = [DailyMenuDB(
            id=20190101, day=1, month=1, year=2019, lunch1='L1', lunch2='L2', dinner1='D1',
            dinner2='D2')]

        dmm = DailyMenusManager()
        dmm.load_from_database()

        dmdb_mock.query.all.assert_called_once_with()
        atm_mock.assert_called_with([DailyMenu(1, 1, 2019, Meal('L1', 'L2'), Meal('D1', 'D2'))])

    @pytest.fixture
    def save_to_database_mocks(self):
        glu_mock = mock.patch(
            'app.menus.core.daily_menus_manager.UpdateControl.get_last_update').start()
        should_update_mock = mock.patch(
            'app.menus.core.daily_menus_manager.UpdateControl.should_update').start()
        logger_mock = mock.patch('app.menus.core.daily_menus_manager.logger').start()

        yield glu_mock, should_update_mock, logger_mock

        mock.patch.stopall()

    @pytest.mark.parametrize('should_update', [True, False])
    def test_save_to_database(self, should_update, save_to_database_mocks):
        glu_mock, should_update_mock, logger_mock = save_to_database_mocks

        should_update_mock.return_value = should_update
        glu_mock.return_value = '[info]'
        menu_mock = mock.Mock()

        dmm = DailyMenusManager()
        dmm.add_to_menus([menu_mock, menu_mock])
        dmm.save_to_database()

        if should_update:
            menu_mock.to_database.assert_called()
            assert menu_mock.to_database.call_count == 2
            logger_mock.debug.assert_called_with('Saving menus to database')
        else:
            logger_mock.info.assert_called_with('Permission denied by UpdateControl (%s)', '[info]')
