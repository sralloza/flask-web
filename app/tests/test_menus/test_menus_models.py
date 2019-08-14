from app.menus.core.structure import DailyMenu, Meal
from app.menus.models import DailyMenuDB


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
