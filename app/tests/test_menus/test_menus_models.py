import sqlite3
from datetime import datetime, timedelta
from unittest import mock

import pytest

from app.menus.core.structure import DailyMenu, Meal
from app.menus.models import DatabaseConnection, UpdateControl
from app.utils import now


class TestDailyMenuDB:
    def test_attributes(self):
        assert hasattr(DailyMenuDB, "id")
        assert hasattr(DailyMenuDB, "day")
        assert hasattr(DailyMenuDB, "month")
        assert hasattr(DailyMenuDB, "year")
        assert hasattr(DailyMenuDB, "lunch1")
        assert hasattr(DailyMenuDB, "lunch2")
        assert hasattr(DailyMenuDB, "dinner1")
        assert hasattr(DailyMenuDB, "dinner2")

    def test_to_normal_daily_menu(self):
        menu_db = DailyMenuDB(
            id="2019-06-06",
            day=6,
            month=6,
            year=2019,
            lunch1="lunch-1",
            lunch2="lunch-2",
            dinner1="dinner-1",
            dinner2="dinner-2",
        )
        menu_normal = DailyMenu(
            day=6,
            month=6,
            year=2019,
            lunch=Meal("lunch-1", "lunch-2"),
            dinner=Meal("dinner-1", "dinner-2"),
        )

        assert menu_db.to_normal_daily_menu() == menu_normal


class TestUpdateControl:
    @pytest.fixture(autouse=True)
    def auto_remove_database(self, reset_database):
        yield

    @pytest.fixture
    def uc_sqlite(self):
        sqlite_mock = mock.patch("app.menus.models.sqlite3", autospec=True).start()
        uc = UpdateControl()

        sqlite_mock.connect.assert_called_once()
        sqlite_mock.connect.return_value.cursor.assert_called_once()

        yield sqlite_mock, uc

        mock.patch.stopall()

    def test_attributes(self):
        uc = UpdateControl()
        assert hasattr(uc, "session")
        assert hasattr(uc, "cursor")

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

    @mock.patch("app.menus.models.sqlite3", autospec=True)
    def test_context_manager(self, sqlite_mock):
        assert hasattr(UpdateControl, "__enter__")
        assert hasattr(UpdateControl, "__exit__")

        with UpdateControl() as uc:
            assert isinstance(uc, UpdateControl)

        sqlite_mock.connect.assert_called_once()
        sqlite_mock.connect.return_value.cursor.assert_called_once()

        cursor_mock = sqlite_mock.connect.return_value.cursor.return_value
        cursor_mock.close.assert_called_once()
        sqlite_mock.connect.return_value.close.assert_called_once()

    class TestShouldUpdate:
        @pytest.fixture(scope="function", autouse=True)
        def db_connection(self):
            connection = sqlite3.connect(":memory:")
            yield connection
            connection.close()

        @pytest.fixture
        def glu_mock(self):
            glu_mock = mock.patch(
                "app.menus.models.UpdateControl.get_last_update",
                spec=UpdateControl.get_last_update,
            ).start()
            yield glu_mock
            mock.patch.stopall()

        def test_yes_1(self, glu_mock, reset_database):
            glu_mock.return_value = datetime(2000, 1, 1, 0, 0, 0)

            assert UpdateControl.should_update() is True

        def test_yes_2(self, glu_mock):
            glu_mock.return_value = now() - timedelta(minutes=20)

            assert UpdateControl.should_update() is True

        def test_yes_3(self, glu_mock):
            glu_mock.return_value = now() - timedelta(minutes=21)

            assert UpdateControl.should_update() is True

        def test_no(self, glu_mock):
            glu_mock.return_value = now() - timedelta(minutes=19)

            assert UpdateControl.should_update() is False

        @mock.patch(
            "app.menus.models.UpdateControl.set_last_update",
            spec=UpdateControl.set_last_update,
        )
        @mock.patch(
            "app.menus.models.UpdateControl.get_last_update",
            spec=UpdateControl.get_last_update,
            return_value=datetime(2000, 1, 1),
        )
        def test_set_after(self, glu_mock, slu_mock):
            assert UpdateControl.should_update() is True
            slu_mock.assert_called_once_with()

            glu_mock.return_value = now()

            assert UpdateControl.should_update() is False
            assert slu_mock.call_count == 1

    @mock.patch("app.menus.models.now", autospec=True)
    def test_set_last_update(self, now_mock):
        expected = "2019-05-18 17:25:15"
        now_mock.return_value.strftime.return_value = expected
        with UpdateControl() as uc:
            uc.set_last_update()
            uc.cursor.execute("SELECT datetime FROM update_control")
            data = uc.cursor.fetchall()
            assert data[0][0] == expected

    def test_get_last_update_good(self):
        with UpdateControl() as uc:
            uc.set_last_update()
            dt = uc.get_last_update()
            assert dt.date() == now().date()

    def test_get_last_update_too_many_items(self):
        with UpdateControl() as uc:
            uc.cursor.execute(
                "INSERT INTO update_control VALUES (?)", ["2000-01-01 10:10:10"]
            )
            uc.cursor.execute(
                "INSERT INTO update_control VALUES (?)", ["2000-01-01 11:11:11"]
            )
            uc.session.commit()

            with pytest.raises(
                    sqlite3.DatabaseError, match="Too many datetimes stored"
            ):
                uc.get_last_update()

    def test_get_last_update_invalid_format(self):
        with UpdateControl() as uc:
            uc.cursor.execute(
                "INSERT INTO update_control VALUES (?)", ["invalid-format"]
            )
            uc.session.commit()

        assert UpdateControl.get_last_update() == UpdateControl.MIN_DATETIME

        with UpdateControl() as uc:
            uc.session.commit()
            uc.cursor.execute("SELECT * FROM update_control")
            data = uc.cursor.fetchall()
            assert data == []
