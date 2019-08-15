import datetime
import sqlite3

from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()


# noinspection PyUnresolvedReferences
class DailyMenuDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    lunch1 = db.Column(db.String(200))
    lunch2 = db.Column(db.String(200))
    dinner1 = db.Column(db.String(200))
    dinner2 = db.Column(db.String(200))

    def to_normal_daily_menu(self):
        from .core.structure import DailyMenu as NormalDailyMenu, Meal
        day = int(self.day)
        month = int(self.month)
        year = int(self.year)
        lunch = Meal(self.lunch1, self.lunch2)
        dinner = Meal(self.dinner1, self.dinner2)

        return NormalDailyMenu(day=day, month=month, year=year, lunch=lunch, dinner=dinner)


class UpdateControl:
    def __init__(self):
        self.session = sqlite3.connect(Config.DATABASE_PATH)
        self.cursor = self.session.cursor()
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS update_control (
                datetime TEXT NOT NULL
                )""")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.cursor.close()
        self.session.close()

    def commit(self):
        self.session.commit()

    @staticmethod
    def should_update(minutes=20):
        last_update = UpdateControl.get_last_update()
        today = datetime.datetime.today()
        today.replace(microsecond=0)
        delta = datetime.timedelta(minutes=minutes)
        return last_update + delta <= today

    @staticmethod
    def set_last_update():
        # TODO: add argument dt
        with UpdateControl() as uc:
            dt = datetime.datetime.today()
            dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')

            last_update = uc.get_last_update()

            if last_update is None:
                uc.cursor.execute('INSERT INTO update_control VALUES (?)', (dt_str,))
            else:
                uc.cursor.execute('UPDATE update_control SET datetime=?', (dt_str,))

            # To check that no more than one entry exists in the database
            uc.get_last_update()
            uc.commit()

    @staticmethod
    def get_last_update():
        with UpdateControl() as uc:
            uc.cursor.execute('select datetime from update_control')
            data = uc.cursor.fetchall()

            if len(data) == 0:
                return None

            if len(data) > 1:
                raise sqlite3.DatabaseError(f'Too many datetimes stored ({len(data)})')

            try:
                return datetime.datetime.strptime(data[0][0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                uc.cursor.execute('DELETE FROM update_control')
                return datetime.datetime(2050, 12, 31)
