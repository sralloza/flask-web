import sqlite3
from datetime import datetime, timedelta
from unittest import mock

import pytest

from app.menus.core.structure import DailyMenu, Meal
from app.menus.models import (
    DailyMenusDatabaseController,
    DatabaseConnection,
    UpdateControl,
)
from app.utils import now


@mock.patch("app.menus.models.DatabaseConnection")
class TestDailyMenusDatabaseController:
    def test_list_menus(self, mock_db_connection):
        # It should use a context manager (__enter__)
        mock_db_connection.return_value.__enter__.return_value.fetch_all.return_value = [
            [1, 1, 1998, "cm-11", "cm-12", "cn-11", "cn-12"],
            [2, 1, 1998, "cm-21", "cm-22", "cn-21", "cn-22"],
        ]

        menus = DailyMenusDatabaseController.list_menus()
        assert menus == [
            DailyMenu(1, 1, 1998, Meal("cm-11", "cm-12"), Meal("cn-11", "cn-12")),
            DailyMenu(2, 1, 1998, Meal("cm-21", "cm-22"), Meal("cn-21", "cn-22")),
        ]

    @pytest.mark.parametrize("table_exists", [True, False])
    @pytest.mark.parametrize("errors", [True, False])
    @mock.patch("app.menus.models.DailyMenusDatabaseController.save_daily_menu")
    def test_backwards_compatibility(self, mock_save, mock_db, table_exists, errors):
        # Use of context manager (__enter__)
        mock_connection = mock_db.return_value.__enter__.return_value
        mock_connection.fetch_all.return_value = [
            [1, 1, 1998, "cm-11", "cm-12", "cn-11", "cn-12"],
            [2, 1, 1998, "cm-21", "cm-22", "cn-21", "cn-22"],
            [3, 1, 1998, "cm-21", "cm-22", "cn-21", "cn-22"],
            [4, 1, 1998, "cm-21", "cm-22", "cn-21", "cn-22"],
            [5, 1, 1998, "cm-21", "cm-22", "cn-21", "cn-22"],
        ]
        if not table_exists:
            mock_connection.execute.side_effect = sqlite3.OperationalError

        if errors:
            mock_save.return_value = False
        else:
            mock_save.return_value = True

        DailyMenusDatabaseController.backwards_compatibility()

        if not table_exists:
            mock_connection.fetch_all.assert_not_called()
        else:
            mock_connection.fetch_all.assert_called()
            mock_save.assert_called()
            assert mock_save.call_count == 5

            if errors:
                assert mock.call("DROP TABLE 'daily_menudb'") not in mock_connection.execute.call_args_list
            else:
                mock_connection.execute.assert_called_with("DROP TABLE 'daily_menudb'")

    @pytest.mark.parametrize("back_compat", [True, False])
    @pytest.mark.parametrize("error", [True, False])
    @mock.patch("app.menus.models.DailyMenusDatabaseController.backwards_compatibility")
    def test_save_daily_menu(self, mock_back_compat, mock_db, back_compat, error):
        menu = DailyMenu(1, 2, 2003, Meal("a", "b"), Meal("c", "d"))
        # Use of context manager (__enter__)
        mock_connection = mock_db.return_value.__enter__.return_value

        if error:
            mock_connection.execute.side_effect = sqlite3.IntegrityError

        result = DailyMenusDatabaseController.save_daily_menu(
            menu, backwards_compatibility=back_compat
        )

        mock_connection.execute.assert_called_with(
            "INSERT INTO 'daily_menus' VALUES (?,?,?,?,?,?,?,?)",
            (20030201, 1, 2, 2003, "a", "b", "c", "d"),
        )

        if error:
            assert result is False
            mock_connection.commit.assert_not_called()
        else:
            assert result is True
            mock_connection.commit.assert_called()

        if back_compat:
            mock_back_compat.assert_called()
        else:
            mock_back_compat.assert_not_called()

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
        assert hasattr(uc, "connection")

        assert isinstance(uc.connection, DatabaseConnection)

        uc.connection.close()

    def test_close(self, uc_sqlite):
        sqlite_mock, uc = uc_sqlite
        uc.close()

        cursor_mock = sqlite_mock.connect.return_value.cursor.return_value
        cursor_mock.close.assert_called_once()
        sqlite_mock.connect.return_value.close.assert_called_once()

    def test_commit(self, uc_sqlite):
        sqlite_mock, uc = uc_sqlite
        uc.commit()

        sqlite_mock.connect.return_value.commit.assert_called()

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
            uc.connection.execute("SELECT datetime FROM update_control")
            data = uc.connection.fetch_all()
            assert data[0][0] == expected

    def test_get_last_update_good(self):
        with UpdateControl() as uc:
            uc.set_last_update()
            dt = uc.get_last_update()
            assert dt.date() == now().date()

    def test_get_last_update_too_many_items(self):
        with UpdateControl() as uc:
            uc.connection.execute(
                "INSERT INTO update_control VALUES (?)", ["2000-01-01 10:10:10"]
            )
            uc.connection.execute(
                "INSERT INTO update_control VALUES (?)", ["2000-01-01 11:11:11"]
            )
            uc.connection.commit()

            with pytest.raises(
                sqlite3.DatabaseError, match="Too many datetimes stored"
            ):
                uc.get_last_update()

    def test_get_last_update_invalid_format(self):
        with UpdateControl() as uc:
            uc.connection.execute(
                "INSERT INTO update_control VALUES (?)", ["invalid-format"]
            )
            uc.connection.commit()

        assert UpdateControl.get_last_update() == UpdateControl.MIN_DATETIME

        with UpdateControl() as uc:
            uc.connection.commit()
            uc.connection.execute("SELECT * FROM update_control")
            data = uc.connection.fetch_all()
            assert data == []
