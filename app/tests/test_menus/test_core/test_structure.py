import datetime
import itertools

import pytest

from app.menus.core.structure import Index as Index
from app.menus.core.structure import Meal, MealError, DailyMenu, MealWarning, Combined, LunchState

# Test data
mydate = (datetime.date(2019, 1, 1), None)
lunch = (Meal('lunch1', 'lunch2'), None)
dinner = (Meal('dinner1', 'dinner2'), None)
states = ('LUNCH', 'DINNER', None)


def gen_indexes():
    _params = list(itertools.product(lunch, dinner, mydate, states))
    return [Index(*a) for a in _params]


class TestIndex:
    _commit = [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    _emtpy = [0, 0, 2, 0, 0, 2, 0, 1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 2, 1, 1, 2, 1, 1, 2]
    _decide = [0, 0, 2, 0, 0, 2, 0, 1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 2, 1, 1, 2, 1, 1, 2]
    _dicts = [3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]

    @pytest.mark.parametrize('index, commit', list(zip(gen_indexes(), _commit)))
    def test_commit(self, index, commit):
        assert index.commit() == bool(commit)

    @pytest.mark.parametrize('index, empty', list(zip(gen_indexes(), _emtpy)))
    def test_is_actual_meal_empty(self, index, empty):
        if empty == 2:
            with pytest.raises(MealError, match='meal_type is None'):
                assert index.is_current_meal_empty()
        else:
            assert index.is_current_meal_empty() == bool(empty)

    @pytest.mark.parametrize('index, decide', list(zip(gen_indexes(), _decide)))
    def test_decide(self, index, decide):
        if decide == 2:
            with pytest.raises(MealError, match='meal_type is None'):
                assert index.is_current_meal_empty()
        elif decide == 1:
            assert index.decide('hello-world')
            assert index.get_first() == 'hello-world'
        else:
            with pytest.warns(MealWarning, match='Could not decide: hello-world'):
                assert not index.decide('hello-world')

    def test_set_state(self):
        i = Index()
        i.set_state('LUNCH')
        assert i.state == LunchState.LUNCH

        i.set_state('DINNER')
        assert i.state == LunchState.DINNER

        with pytest.raises(ValueError, match='Invalid meal type'):
            i.set_state('DUMMY')

        with pytest.raises(ValueError, match='Invalid meal type'):
            i.set_state('LAUNCH')

    def test_set_first(self):
        i = Index()

        with pytest.raises(RuntimeError, match='Meal type not set'):
            i.set_first('dummy')

        i.set_state('LUNCH')
        i.set_first('test first lunch')
        assert i.lunch.p1 == 'test first lunch'

        i.set_state('DINNER')
        i.set_first('test first dinner')
        assert i.dinner.p1 == 'test first dinner'

        i.set_first('')
        assert i.dinner.p1 == 'test first dinner'

    def test_get_first(self):
        i = Index()

        i.set_state('LUNCH')
        i.set_first('test first lunch')
        assert i.get_first() == 'test first lunch'

        i.set_state('DINNER')
        i.set_first('test first dinner')
        assert i.get_first() == 'test first dinner'

        i.set_first('')
        assert i.get_first() == 'test first dinner'

    def test_set_second(self):
        i = Index()

        with pytest.raises(RuntimeError, match='Meal type not set'):
            i.set_second('dummy')

        i.set_state('LUNCH')
        i.set_second('test second lunch')
        assert i.lunch.p2 == 'test second lunch'

        i.set_state('DINNER')
        i.set_second('test second dinner')
        assert i.dinner.p2 == 'test second dinner'

        i.set_second('')
        assert i.dinner.p2 == 'test second dinner'

    def test_get_second(self):
        i = Index()

        i.set_state('LUNCH')
        i.set_second('test first lunch')
        assert i.get_second() == 'test first lunch'

        i.set_state('DINNER')
        i.set_second('test first dinner')
        assert i.get_second() == 'test first dinner'

        i.set_second('')
        assert i.get_second() == 'test first dinner'

    @pytest.mark.parametrize('index, dictcode', list(zip(gen_indexes(), _dicts)))
    def test_to_dict(self, index, dictcode):
        # 0 -> none, 1 -> dinner, 2 -> lunch, 3 -> both

        if dictcode == 0:
            assert index.to_dict() == {'lunch': Meal(), 'dinner': Meal()}
        elif dictcode == 1:
            assert index.to_dict() == {'lunch': Meal(), 'dinner': dinner[0]}
        elif dictcode == 2:
            assert index.to_dict() == {'lunch': lunch[0], 'dinner': Meal()}
        elif dictcode == 3:
            assert index.to_dict() == {'lunch': lunch[0], 'dinner': dinner[0]}
        else:
            assert 0, 'Invalid dictcode state: %s' % dictcode


def gen_meals():
    p1 = ('meal_1', None)
    p2 = ('meal_2', None)

    _params = list(itertools.product(p1, p2))
    return [Meal(*a) for a in _params]


class TestMeal:
    _is_empty = [0, 0, 0, 1]

    @pytest.mark.parametrize('meal, is_empty', list(zip(gen_meals(), _is_empty)))
    def test_is_empty(self, meal, is_empty):
        if is_empty == 1:
            assert meal.is_empty()
        else:
            assert not meal.is_empty()

    def test_update(self):
        m1 = Meal()
        m2 = Meal()
        m3 = Meal()
        m4 = Meal()

        m1.update(p1=None, p2=None)

        assert m1.p1 is None
        assert m1.p2 is None

        m2.update(p1='meal_1', p2=None)
        assert m2.p1 == 'meal_1'
        assert m2.p2 is None

        m3.update(p1=None, p2='meal_2')
        assert m3.p1 is None
        assert m3.p2 == 'meal_2'

        m4.update(p1='meal_1', p2='meal_2')
        assert m4.p1 == 'meal_1'
        assert m4.p2 == 'meal_2'

        with pytest.raises(ValueError, match="Invalid arguments for Meal: {'foo': 'bar'}"):
            m1.update(foo='bar', p1='new_meal')

        assert m1.p1 == 'new_meal'

    def test_force_update(self):
        meal = Meal()
        meal.update(p1='p1', p2='p2')
        assert meal.p1 == 'p1'
        assert meal.p2 == 'p2'

        meal.update(p1='new-1', p2='new-2')
        assert meal.p1 == 'new-1'
        assert meal.p2 == 'new-2'

    def test_strip(self):
        m = Meal(p1=' mEaL-1 ', p2='   MeaL-2   ')
        m.strip()

        assert m.p1 == 'meal-1'
        assert m.p2 == 'meal-2'


class TestCombined:
    def test_attributes(self):
        combined = Combined('hello')
        assert combined.p1 == 'hello'
        assert combined.p2 is None

    def test_is_empty(self):
        combined_1 = Combined('hello')
        combined_2 = Combined()
        assert not combined_1.is_empty()
        assert combined_2.is_empty()

    def test_update(self):
        combined = Combined()
        combined.update(p1='hello')
        assert combined.p1 == 'hello'

        with pytest.raises(ValueError, match='Invalid arguments for Combined'):
            combined.update(p2='world')


def gen_daily_menus():
    lunch = (Meal(), Meal(p1='lunch-1'), Meal(p1='lunch-1', p2='lunch-2'))
    dinner = (Meal(), Meal(p1='dinner-1'), Meal(p1='dinner-1', p2='dinner-2'))

    product = list(itertools.product(lunch, dinner))
    dates = [(x, 1, 2019) for x in range(1, len(product) + 1)]
    return [DailyMenu(*x, *k) for x, k in zip(dates, product)]


class TestDailyMenu:
    esp_eng = (
        ('12 febrero 2016 martes', '12 february 2016 tuesday'),
        ('13 de diciembre de 2016 (martes)', '13 de december de 2016 (tuesday)'),
        ('13 de diciembre de 2017 (miércoles)', '13 de december de 2017 (wednesday)'),
        ('13 de enero de 2017 (viernes)', '13 de january de 2017 (friday)'),
        ('14 de julio de 2017 (viernes)', '14 de july de 2017 (friday)'),
        ('15 de agosto de 2017 (martes)', '15 de august de 2017 (tuesday)'),
        ('16 de octubre de 2017 (lunes)', '16 de october de 2017 (monday)'),
        ('16 enero viernes', '16 january friday'),
        ('22 de septiembre de 2017 (viernes)', '22 de september de 2017 (friday)'),
        ('23 de febrero de 2017 (jueves)', '23 de february de 2017 (thursday)'),
        ('28 de junio de 2017 (miércoles)', '28 de june de 2017 (wednesday)'),
        ('30 de mayo de 2017 (martes)', '30 de may de 2017 (tuesday)'),
        ('6 de marzo de 2017 (lunes)', '6 de march de 2017 (monday)'),
        ('7 de noviembre de 2017 (martes)', '7 de november de 2017 (tuesday)'),
        ('9 de abril de 2017 (domingo)', '9 de april de 2017 (sunday)'),
        ('día: 25 de febrero de 2019 (lunes)', 'día: 25 de february de 2019 (monday)'),
    )

    datetimes = (
        ('Día: 13 de diciembre de 2016 (martes)', datetime.date(2016, 12, 13)),
        ('Día: 13 de enero de 2017 (viernes)', datetime.date(2017, 1, 13)),
        ('Día: 23 de febrero de 2017 (jueves)', datetime.date(2017, 2, 23)),
        ('Día: 6 de marzo de 2017 (lunes)', datetime.date(2017, 3, 6)),
        ('Día: 9 de abril de 2017 (domingo)', datetime.date(2017, 4, 9)),
        ('Día: 30 de mayo de 2017 (martes)', datetime.date(2017, 5, 30)),
        ('Día: 28 de junio de 2017 (miércoles)', datetime.date(2017, 6, 28)),
        ('Día: 14 de julio de 2017 (viernes)', datetime.date(2017, 7, 14)),
        ('Día: 15 de agosto de 2017 (martes)', datetime.date(2017, 8, 15)),
        ('Día: 22 de septiembre de 2017 (viernes)', datetime.date(2017, 9, 22)),
        ('Día: 16 de octubre de 2017 (lunes)', datetime.date(2017, 10, 16)),
        ('Día: 7 de noviembre de 2017 (martes)', datetime.date(2017, 11, 7)),
        ('Día: 13 de diciembre de 2017 (miércoles)', datetime.date(2017, 12, 13)),
        (datetime.date(2016, 12, 13), datetime.date(2016, 12, 13)),
        (datetime.date(2017, 1, 13), datetime.date(2017, 1, 13)),
        (datetime.date(2017, 2, 23), datetime.date(2017, 2, 23)),
        (datetime.date(2017, 3, 6), datetime.date(2017, 3, 6)),
        (datetime.date(2017, 4, 9), datetime.date(2017, 4, 9)),
        (datetime.date(2017, 5, 30), datetime.date(2017, 5, 30)),
        (datetime.date(2017, 6, 28), datetime.date(2017, 6, 28)),
        (datetime.date(2017, 7, 14), datetime.date(2017, 7, 14)),
        (datetime.date(2017, 8, 15), datetime.date(2017, 8, 15)),
        (datetime.date(2017, 9, 22), datetime.date(2017, 9, 22)),
        (datetime.date(2017, 10, 16), datetime.date(2017, 10, 16)),
        (datetime.date(2017, 11, 7), datetime.date(2017, 11, 7)),
        (datetime.date(2017, 12, 13), datetime.date(2017, 12, 13)),
    )

    format_dates = (
        (datetime.date(2016, 12, 13), '13 de diciembre de 2016 (martes)'),
        (datetime.date(2017, 1, 13), '13 de enero de 2017 (viernes)'),
        (datetime.date(2017, 2, 23), '23 de febrero de 2017 (jueves)'),
        (datetime.date(2017, 3, 6), '06 de marzo de 2017 (lunes)'),
        (datetime.date(2017, 4, 9), '09 de abril de 2017 (domingo)'),
        (datetime.date(2017, 5, 30), '30 de mayo de 2017 (martes)'),
        (datetime.date(2017, 6, 28), '28 de junio de 2017 (miércoles)'),
        (datetime.date(2017, 7, 14), '14 de julio de 2017 (viernes)'),
        (datetime.date(2017, 8, 15), '15 de agosto de 2017 (martes)'),
        (datetime.date(2017, 9, 22), '22 de septiembre de 2017 (viernes)'),
        (datetime.date(2017, 10, 16), '16 de octubre de 2017 (lunes)'),
        (datetime.date(2017, 11, 7), '07 de noviembre de 2017 (martes)'),
        (datetime.date(2017, 12, 13), '13 de diciembre de 2017 (miércoles)'),
    )

    _to_str = (
        '1-martes-0-0', '2-miércoles-0-1', '3-jueves-0-2', '4-viernes-1-0',
        '5-sábado-1-1',
        '6-domingo-1-2', '7-lunes-2-0', '8-martes-2-1', '9-miércoles-2-2'
    )

    @pytest.mark.parametrize('esp, eng', esp_eng)
    def test_e_to_s(self, esp, eng):
        assert DailyMenu.e_to_s(eng) == esp

    @pytest.mark.parametrize('esp, eng', esp_eng)
    def test_s_to_e(self, esp, eng):
        assert DailyMenu.s_to_e(esp) == eng

    @pytest.mark.parametrize('dm, str_code', list(zip(gen_daily_menus(), _to_str)))
    def test_to_string(self, dm, str_code):
        # Code: day-weekday-lunch_code-dinner_code
        # Meals codes: 0 -> emtpy, 1 -> P1, 2 -> P1 & P2

        day, weekday, lunch_code, dinner_code = str_code.split('-')

        day = int(day)
        day_str = f'{day:02d} de enero de 2019 ({weekday})\n'

        lunch_code = int(lunch_code)
        lunch_str = ''
        if lunch_code != 0:
            lunch_str += ' - Comida\n'
            lunch_str += '   - lunch-1\n'
        if lunch_code == 2:
            lunch_str += '   - lunch-2\n'

        dinner_code = int(dinner_code)
        dinner_str = ''
        if dinner_code != 0:
            dinner_str += ' - Cena\n'
            dinner_str += '   - dinner-1\n'
        if dinner_code == 2:
            dinner_str += '   - dinner-2\n'

        total_str = day_str + lunch_str + dinner_str

        assert dm.to_string() == total_str

    @pytest.mark.parametrize('dm, str_code', list(zip(gen_daily_menus(), _to_str)))
    def test_to_html(self, dm, str_code):
        # Code: day-weekday-lunch_code-dinner_code
        # Meals codes: 0 -> emtpy, 1 -> P1, 2 -> P1 & P2

        day, weekday, lunch_code, dinner_code = str_code.split('-')

        day = int(day)
        day_str = f'{day:02d} de enero de 2019 ({weekday})<br>'

        lunch_code = int(lunch_code)
        lunch_str = ''
        if lunch_code != 0:
            lunch_str += ' - Comida<br>'
            lunch_str += '   - lunch-1<br>'
        if lunch_code == 2:
            lunch_str += '   - lunch-2<br>'

        dinner_code = int(dinner_code)
        dinner_str = ''
        if dinner_code != 0:
            dinner_str += ' - Cena<br>'
            dinner_str += '   - dinner-1<br>'
        if dinner_code == 2:
            dinner_str += '   - dinner-2<br>'

        total_str = day_str + lunch_str + dinner_str

        assert dm.to_html() == total_str

    @pytest.mark.parametrize('dt_to_parse, dt_expected', datetimes)
    def test_from_datetime(self, dt_to_parse, dt_expected):
        assert DailyMenu.from_datetime(dt_to_parse).date == dt_expected

    @pytest.mark.parametrize('dt_to_parse, str_expected', format_dates)
    def test_format_date(self, dt_to_parse, str_expected):
        assert DailyMenu.from_datetime(dt_to_parse).format_date() == str_expected

    def test_update(self):
        dm = DailyMenu(1, 1, 2019)

        lunch = Meal('lunch-1', 'lunch-2')
        dinner = Meal('dinner-1', 'dinner-2')

        dm.update(lunch=lunch, dinner=dinner)

        assert dm.lunch == lunch
        assert dm.dinner == dinner

        with pytest.raises(ValueError, match='Lunch must be Meal'):
            dm.update(lunch='peter')

        with pytest.raises(ValueError, match='Dinner must be Meal'):
            dm.update(dinner='pan')

        dm.update(lunch1='lunch1', lunch2='lunch2', dinner1='dinner1', dinner2='dinner2')
        assert dm.lunch == Meal('lunch1', 'lunch2')
        assert dm.dinner == Meal('dinner1', 'dinner2')
