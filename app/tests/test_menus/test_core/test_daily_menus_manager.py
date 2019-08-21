import json
import random
from datetime import date, datetime
from unittest import mock

import pytest

from app.config import Config
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

    @pytest.fixture
    def load_from_menus_urls_mocks(self):
        gmu_mock = mock.patch('app.menus.core.daily_menus_manager.get_menus_urls').start()
        worker_mock = mock.patch('app.menus.core.daily_menus_manager.Worker').start()
        logger_mock = mock.patch('app.menus.core.daily_menus_manager.logger').start()

        yield gmu_mock, worker_mock, logger_mock

        mock.patch.stopall()

    def test_load_from_menus_urls(self, load_from_menus_urls_mocks):
        gmu_mock, worker_mock, logger_mock = load_from_menus_urls_mocks

        gmu_mock.return_value = ['url-1', 'url-2', 'url-3', 'url-4']

        dmm = DailyMenusManager()
        dmm.load_from_menus_urls()

        logger_mock.debug.assert_called_with('Loading from menus urls')
        worker_mock.assert_any_call('url-1', dmm)
        worker_mock.assert_any_call('url-2', dmm)
        worker_mock.assert_any_call('url-3', dmm)
        worker_mock.assert_any_call('url-4', dmm)
        worker_mock.return_value.start.assert_called()
        assert worker_mock.return_value.start.call_count == 4
        worker_mock.return_value.join.assert_called()
        assert worker_mock.return_value.join.call_count == 4

    @pytest.fixture
    def process_url_mocks(self):
        logger_mock = mock.patch('app.menus.core.daily_menus_manager.logger').start()
        requests_mock = mock.patch('app.menus.core.daily_menus_manager.requests').start()

        yield logger_mock, requests_mock

        mock.patch.stopall()

    @pytest.mark.parametrize('number', [1, 2, 3, 4, 5, 6, 7])
    def test_process_url_process_text_update_menu(self, process_url_mocks, number):
        root_path = Config.TEST_DATA_PATH / 'menus-html' / f'{number}'
        html_path = root_path / 'html.html'
        json_path = root_path / 'data.json'

        with html_path.open(encoding='utf-8') as f:
            file_content = f.read()

        logger_mock, requests_mock = process_url_mocks
        requests_mock.get.return_value.text = file_content

        dmm = DailyMenusManager()
        dmm.process_url('https://example.com')
        real_json = dmm.to_json()

        with json_path.open('r', encoding='utf-8') as f:
            json_expected = json.load(f)

        assert len(dmm) == len(json_expected)
        assert real_json == json_expected

        # path = Path('D:/') / (number + '.json')
        # with path.open('wt', encoding='utf-8') as f:
        #     f.write(json.dumps(dmm.to_json(), ensure_ascii=False))
