"""Database models for application."""
import logging
import sqlite3
from datetime import datetime, timedelta

from flask import current_app

from app.utils import now

logger = logging.getLogger(__name__)


class DailyMenusDatabaseController:
    """Interface to list, save and remove menus using a sqlite database."""

    @staticmethod
    def list_menus():
        """Returns a list with menus stored in the database.

        Returns:
            list of DailyMenu: menus stored in the database.
        """
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
        """Saves a menu in the database.

        Args:
            daily_menu (DailyMenu): menu to saveself.

        Returns:
            bool: True if it has been saved. False otherwise.
        """
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
        """Removes a menu from the database.

        Args:
            daily_menu (DailyMenu): menu to remove from the database.

        Returns:
            bool: True if it was deleted. False otherwise.
        """
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
    """Interface for raw database connections."""

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
        """Closes the database connection."""
        self.cursor.close()
        self.connection.close()

    def commit(self):
        """Saves changes to the database."""
        self.connection.commit()

    def execute(self, *args, **kwargs):
        """Executes a SQL order."""
        return self.cursor.execute(*args, **kwargs)

    def fetch_all(self):
        """Returns all the data stored in the database."""
        return self.cursor.fetchall()

    def ensure_tables(self):
        """Executes a SQL script to ensure the existance of the sqlite table."""
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
    """Manager class that decides when is the database can be updated."""

    MIN_DATETIME = datetime.min

    def __init__(self):
        self.connection = DatabaseConnection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Closes the connection with the database."""
        self.connection.close()

    def commit(self):
        """Saves the changes made to the database."""
        self.connection.commit()

    @staticmethod
    def should_update(minutes=20):
        """Returns whether or not the database can be updated.

        Notes:
            When the database is updated, the method UpdateControl.set_last_update()
                must be called

        Args:
            minutes (int, optional): Minimum minutes between updates. Defaults to 20.

        Returns:
            bool: True if the database can be updated. False otherwise
        """
        last_update = UpdateControl.get_last_update()
        today = now()
        today.replace(microsecond=0)
        delta = timedelta(minutes=minutes)
        should_update = last_update + delta <= today

        logger.debug("Should Update decision: %s (%s)", should_update, last_update)

        return should_update

    @staticmethod
    def set_last_update():
        """Indicates that the database just have been updated. This
        method will save the exact time when it was called to the
        database, so UpdateControl.should_update() can make a choice.
        """
        with UpdateControl() as update_control:
            dt_str = now().strftime("%Y-%m-%d %H:%M:%S")

            last_update = update_control.get_last_update()

            if last_update is UpdateControl.MIN_DATETIME:
                update_control.connection.execute(
                    "INSERT INTO update_control VALUES (?)", (dt_str,)
                )
            else:
                update_control.connection.execute(
                    "UPDATE update_control SET datetime=?", (dt_str,)
                )

            # To check that no more than one entry exists in the database
            update_control.get_last_update()
            update_control.commit()

    @staticmethod
    def get_last_update():
        """Returns the datetime when the database was last updated.

        Raises:
            sqlite3.DatabaseError: If there are multiple datetimes stored
                in the database, which by design can't - but errors happens,
                so here we are.

        Returns:
            datetime.datetime: datetime of the last update.
        """
        with UpdateControl() as update_control:
            update_control.connection.execute("select datetime from update_control")
            data = update_control.connection.fetch_all()

            if len(data) == 0:
                return update_control.MIN_DATETIME

            if len(data) > 1:
                raise sqlite3.DatabaseError(f"Too many datetimes stored ({len(data)})")

            try:
                return datetime.strptime(data[0][0], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                update_control.connection.execute("DELETE FROM update_control")
                update_control.commit()
                return update_control.MIN_DATETIME
