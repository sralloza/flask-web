import sqlite3
from datetime import datetime, timedelta
from unittest import mock

import pytest

from app import app
from app.menus.core.structure import DailyMenu, Meal
from app.menus.models import DailyMenuDB, UpdateControl


class TestDailyMenuDB:
    def test_attributes(self):
        assert hasattr(DailyMenuDB, 'id')
        assert hasattr(DailyMenuDB, 'day')
        assert hasattr(DailyMenuDB, 'month')
        assert hasattr(DailyMenuDB, 'year')
        assert hasattr(DailyMenuDB, 'lunch1')
        assert hasattr(DailyMenuDB, 'lunch2')
        assert hasattr(DailyMenuDB, 'dinner1')
        assert hasattr(DailyMenuDB, 'dinner2')

    def test_to_normal_daily_menu(self):
        menu_db = DailyMenuDB(id='2019-06-06', day=6, month=6, year=2019, lunch1='L1', lunch2='L2',
                              dinner1='D1', dinner2='D2')
        menu_normal = DailyMenu(day=6, month=6, year=2019, lunch=Meal('L1', 'L2'),
                                dinner=Meal('D1', 'D2'))

        assert menu_db.to_normal_daily_menu() == menu_normal


class TestUpdateControl:
    @pytest.fixture
    def uc_sqlite(self):
        sqlite_mock = mock.patch('app.menus.models.sqlite3').start()
        uc = UpdateControl()

        sqlite_mock.connect.assert_called_once()
        sqlite_mock.connect.return_value.cursor.assert_called_once()

        yield sqlite_mock, uc

        mock.patch.stopall()

    def test_attributes(self):
        uc = UpdateControl()
        assert hasattr(uc, 'session')
        assert hasattr(uc, 'cursor')

        assert type(uc.session) == sqlite3.Connection
        assert type(uc.cursor) == sqlite3.Cursor

        uc.cursor.close()
        uc.session.close()

    def test_close(self, uc_sqlite):
        sqlite_mock, uc = uc_sqlite
        uc.close()

        cursor_mock = sqlite_mock.connect.return_value.cursor.return_value
        cursor_mock.close.assert_called_once()
        sqlite_mock.connect.return_value.close.assert_called_once()

    def test_commit(self, uc_sqlite):
        sqlite_mock, uc = uc_sqlite
        uc.commit()

        sqlite_mock.connect.return_value.commit.assert_called_once()

        uc.close()

    @mock.patch('app.menus.models.sqlite3')
    def test_context_manager(self, sqlite_mock):
        assert hasattr(UpdateControl, '__enter__')
        assert hasattr(UpdateControl, '__exit__')

        with UpdateControl() as uc:
            assert isinstance(uc, UpdateControl)

        sqlite_mock.connect.assert_called_once()
        sqlite_mock.connect.return_value.cursor.assert_called_once()

        cursor_mock = sqlite_mock.connect.return_value.cursor.return_value
        cursor_mock.close.assert_called_once()
        sqlite_mock.connect.return_value.close.assert_called_once()


    class TestShouldUpdate:
        @pytest.fixture
        def db_connection(self):
            connection = sqlite3.connect(app.config['DATABASE_PATH'])
            cursor = connection.cursor()
            cursor.execute("DELETE FROM update_control")
            yield connection

        def test_yes_1(self, db_connection):
            cursor = db_connection.cursor()
            cursor.execute('INSERT INTO update_control VALUES (?)', ('2000-01-01 00:00:00',))
            db_connection.commit()
            db_connection.close()

            assert UpdateControl.should_update() is True

        def test_yes_2(self, db_connection):
            cursor = db_connection.cursor()
            today = datetime.today() - timedelta(minutes=20)
            cursor.execute('INSERT INTO update_control VALUES (?)',
                           (today.strftime('%Y-%m-%d %H:%M:%S'),))
            db_connection.commit()
            db_connection.close()

            assert UpdateControl.should_update() is True

        def test_yes_3(self, db_connection):
            cursor = db_connection.cursor()
            today = datetime.today() - timedelta(minutes=21)
            cursor.execute('INSERT INTO update_control VALUES (?)',
                           (today.strftime('%Y-%m-%d %H:%M:%S'),))
            db_connection.commit()
            db_connection.close()

            assert UpdateControl.should_update() is True

        def test_no(self, db_connection):
            cursor = db_connection.cursor()
            today = datetime.today() - timedelta(minutes=19)
            cursor.execute('INSERT INTO update_control VALUES (?)',
                           (today.strftime('%Y-%m-%d %H:%M:%S'),))
            db_connection.commit()
            db_connection.close()

            assert UpdateControl.should_update() is False

    def test_set_last_update(self):
        with UpdateControl() as uc:
            uc.set_last_update()
            expected = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            uc.cursor.execute('SELECT datetime FROM update_control')
            data = uc.cursor.fetchall()
            assert data[0][0] == expected

    def test_get_last_update(self):
        with UpdateControl() as uc:
            uc.set_last_update()
            dt = uc.get_last_update()
            assert dt.date() == datetime.today().date()
