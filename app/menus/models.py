from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# noinspection PyUnresolvedReferences
class DailyMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    lunch1 = db.Column(db.String(200))
    lunch2 = db.Column(db.String(200))
    dinner1 = db.Column(db.String(200))
    dinner2 = db.Column(db.String(200))

    def to_normal_daily_menu(self):
        from .motor.structure import DailyMenu as NormalDailyMenu, Meal
        day = int(self.day)
        month = int(self.month)
        year = int(self.year)
        lunch = Meal(self.lunch1, self.lunch2)
        dinner = Meal(self.dinner1, self.dinner2)

        return NormalDailyMenu(day=day, month=month, year=year, lunch=lunch, dinner=dinner)
