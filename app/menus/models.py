import logging
import sqlite3
from datetime import datetime, timedelta

from flask import current_app

from app.utils import now

logger = logging.getLogger(__name__)


class DailyMenusDatabaseController:
    @staticmethod
    def list_menus():
        from app.menus.core.structure import DailyMenu, Meal

        with DatabaseConnection() as connection:
            connection.execute(
                "SELECT day, month, year, lunch1, lunch2, dinner1, dinner2, url FROM 'daily_menus'"
            )

            return [
                DailyMenu(
                    data[0],
                    data[1],
                    data[2],
                    Meal(*data[3:5]),
                    Meal(*data[5:7]),
                    data[7],
                )
                for data in connection.fetch_all()
            ]

    @classmethod
    def save_daily_menu(cls, daily_menu):
        with DatabaseConnection() as connection:
            data = (
                daily_menu.id,
                daily_menu.day,
                daily_menu.month,
                daily_menu.year,
                daily_menu.lunch.p1,
                daily_menu.lunch.p2,
                daily_menu.dinner.p1,
                daily_menu.dinner.p2,
                daily_menu.url,
            )

            try:
                connection.execute(
                    "INSERT INTO 'daily_menus' VALUES (?,?,?,?,?,?,?,?,?)", data
                )
                connection.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    @classmethod
    def remove_daily_menu(cls, daily_menu):
        with DatabaseConnection() as connection:
            connection.execute(
                "SELECT COUNT(*) FROM 'daily_menus' WHERE id=?", [daily_menu.id]
            )
            menus_number = connection.fetch_all()[0][0]

            if not menus_number:
                return False

            connection.execute("DELETE FROM 'daily_menus' WHERE id=?", [daily_menu.id])
            connection.commit()
            return True


class DatabaseConnection:
    def __init__(self):
        try:
            self.connection = sqlite3.connect(current_app.config["DATABASE_PATH"])
        except TypeError:
            self.connection = sqlite3.connect(
                current_app.config["DATABASE_PATH"].as_posix()
            )

        self.cursor = self.connection.cursor()
        self.ensure_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def commit(self):
        self.connection.commit()

    def execute(self, *args, **kwargs):
        return self.cursor.execute(*args, **kwargs)

    def fetch_all(self):
        return self.cursor.fetchall()

    def ensure_tables(self):
        self.execute(
            """
                CREATE TABLE IF NOT EXISTS 'daily_menus' (
                'id'	INTEGER NOT NULL PRIMARY KEY,
                'day'	INTEGER NOT NULL,
                'month'	INTEGER NOT NULL,
                'year'	INTEGER NOT NULL,
                'lunch1'	VARCHAR ( 200 ),
                'lunch2'	VARCHAR ( 200 ),
                'dinner1'	VARCHAR ( 200 ),
                'dinner2'	VARCHAR ( 200 ),
                'url'       VARCHAR (300)
            );
            """
        )

        self.execute(
            """
                CREATE TABLE IF NOT EXISTS 'update_control' (
                'datetime' VARCHAR (200) NOT NULL
            );
            """
        )
        self.commit()


class UpdateControl:
    MIN_DATETIME = datetime.min

    def __init__(self):
        self.connection = DatabaseConnection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()

    @staticmethod
    def should_update(minutes=20):
        last_update = UpdateControl.get_last_update()
        today = now()
        today.replace(microsecond=0)
        delta = timedelta(minutes=minutes)
        should_update = last_update + delta <= today

        logger.debug("Should Update decision: %s (%s)", should_update, last_update)

        return should_update

    @staticmethod
    def set_last_update():
        # TODO: add argument dt
        with UpdateControl() as uc:
            dt = now()
            dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")

            last_update = uc.get_last_update()

            if last_update is UpdateControl.MIN_DATETIME:
                uc.connection.execute(
                    "INSERT INTO update_control VALUES (?)", (dt_str,)
                )
            else:
                uc.connection.execute("UPDATE update_control SET datetime=?", (dt_str,))

            # To check that no more than one entry exists in the database
            uc.get_last_update()
            uc.commit()

    @staticmethod
    def get_last_update():
        with UpdateControl() as uc:
            uc.connection.execute("select datetime from update_control")
            data = uc.connection.fetch_all()

            if len(data) == 0:
                return uc.MIN_DATETIME

            if len(data) > 1:
                raise sqlite3.DatabaseError(f"Too many datetimes stored ({len(data)})")

            try:
                return datetime.strptime(data[0][0], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                uc.connection.execute("DELETE FROM update_control")
                uc.commit()
                return uc.MIN_DATETIME
