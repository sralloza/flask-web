import datetime

import pytest

from app.new_menus.motor.structure import Meal, MealError, DailyMenu
from app.new_menus.motor.structure import _Index as Index


class TestIndex:

    # noinspection PyAttributeOutsideInit,PyTypeChecker
    @pytest.fixture
    def init(self):
        self.mydate = datetime.date(2019, 1, 1)
        self.lunch = Meal('lunch1', 'lunch2')
        self.dinner = Meal('dinner1', 'dinner2')

        self.i01 = Index(None, None, None, None)
        self.i02 = Index(None, None, None, 'LUNCH')
        self.i03 = Index(None, None, self.mydate, None)
        self.i04 = Index(None, None, self.mydate, 'DINNER')
        self.i05 = Index(None, self.dinner, None, None)
        self.i06 = Index(None, self.dinner, None, 'LUNCH')
        self.i07 = Index(None, self.dinner, self.mydate, None)
        self.i08 = Index(None, self.dinner, self.mydate, 'DINNER')
        self.i09 = Index(self.lunch, None, None, None)
        self.i10 = Index(self.lunch, None, None, 'LUNCH')
        self.i11 = Index(self.lunch, None, self.mydate, None)
        self.i12 = Index(self.lunch, None, self.mydate, 'DINNER')
        self.i13 = Index(self.lunch, self.dinner, None, None)
        self.i14 = Index(self.lunch, self.dinner, None, 'LUNCH')
        self.i15 = Index(self.lunch, self.dinner, self.mydate, None)
        self.i16 = Index(self.lunch, self.dinner, self.mydate, 'DINNER')

        return True

    def test_commit(self, init):
        assert init

        assert not self.i01.commit()
        assert not self.i02.commit()
        assert not self.i03.commit()
        assert not self.i04.commit()
        assert not self.i05.commit()
        assert not self.i06.commit()
        assert not self.i07.commit()
        assert self.i08.commit()
        assert not self.i09.commit()
        assert not self.i10.commit()
        assert not self.i11.commit()
        assert self.i12.commit()
        assert not self.i13.commit()
        assert not self.i14.commit()
        assert not self.i15.commit()
        assert self.i16.commit()

    def test_is_actual_meal_empty(self, init):
        assert init

        assert self.i02.is_actual_meal_empty()
        assert self.i04.is_actual_meal_empty()
        assert self.i06.is_actual_meal_empty()
        assert not self.i08.is_actual_meal_empty()
        assert not self.i10.is_actual_meal_empty()
        assert self.i12.is_actual_meal_empty()
        assert not self.i14.is_actual_meal_empty()
        assert not self.i16.is_actual_meal_empty()

        with pytest.raises(MealError, match='Meal_type is None'):
            assert self.i01.is_actual_meal_empty()
        with pytest.raises(MealError, match='Meal_type is None'):
            assert self.i03.is_actual_meal_empty()
        with pytest.raises(MealError, match='Meal_type is None'):
            assert self.i05.is_actual_meal_empty()
        with pytest.raises(MealError, match='Meal_type is None'):
            assert self.i07.is_actual_meal_empty()
        with pytest.raises(MealError, match='Meal_type is None'):
            assert not self.i09.is_actual_meal_empty()
        with pytest.raises(MealError, match='Meal_type is None'):
            assert not self.i11.is_actual_meal_empty()
        with pytest.raises(MealError, match='Meal_type is None'):
            assert not self.i13.is_actual_meal_empty()
        with pytest.raises(MealError, match='Meal_type is None'):
            assert not self.i15.is_actual_meal_empty()

    def test_decide(self, init):
        assert init

        with pytest.raises(MealError, match='Meal_type is None'):
            self.i01.decide('dummy text')
        with pytest.raises(MealError, match='Meal_type is None'):
            self.i03.decide('dummy text')
        with pytest.raises(MealError, match='Meal_type is None'):
            self.i05.decide('dummy text')
        with pytest.raises(MealError, match='Meal_type is None'):
            self.i07.decide('dummy text')
        with pytest.raises(MealError, match='Meal_type is None'):
            self.i09.decide('dummy text')
        with pytest.raises(MealError, match='Meal_type is None'):
            self.i11.decide('dummy text')
        with pytest.raises(MealError, match='Meal_type is None'):
            self.i13.decide('dummy text')
        with pytest.raises(MealError, match='Meal_type is None'):
            self.i15.decide('dummy text')

        self.i02.decide('dummy text')
        self.i04.decide('dummy text')
        self.i06.decide('dummy text')
        self.i12.decide('dummy text')

        assert self.i02.lunch.p1 == 'dummy text'
        assert self.i04.dinner.p1 == 'dummy text'
        assert self.i06.lunch.p1 == 'dummy text'
        assert self.i12.dinner.p1 == 'dummy text'

        with pytest.warns(UserWarning, match='Could not decide'):
            self.i08.decide('dummy text')
        with pytest.warns(UserWarning, match='Could not decide'):
            self.i10.decide('dummy text')
        with pytest.warns(UserWarning, match='Could not decide'):
            self.i14.decide('dummy text')
        with pytest.warns(UserWarning, match='Could not decide'):
            self.i16.decide('dummy text')

        assert self.i08.dinner.p1 != 'dummy text'
        assert self.i10.lunch.p1 != 'dummy text'
        assert self.i14.lunch.p1 != 'dummy text'
        assert self.i16.dinner.p1 != 'dummy text'

    def test_set_meal_type(self):
        i = Index()
        i.set_state('LUNCH')
        assert i.meal_type == 'LUNCH'

        i.set_state('DINNER')
        assert i.meal_type == 'DINNER'

        with pytest.raises(ValueError, match='Invalid meal type'):
            i.set_state('DUMMY')

        with pytest.raises(ValueError, match='Invalid meal type'):
            i.set_state('LAUNCH')

    def test_set_first(self):
        i = Index()

        with pytest.raises(ValueError, match='Invalid meal type'):
            i.set_first('dummy')

        i.set_state('LUNCH')
        i.set_first('test first lunch')
        assert i.lunch.p1 == 'test first lunch'

        i.set_state('DINNER')
        i.set_first('test first dinner')
        assert i.dinner.p1 == 'test first dinner'

        i.set_first('')
        assert i.dinner.p1 == 'test first dinner'

    def test_set_second(self):
        i = Index()

        with pytest.raises(ValueError, match='Invalid meal type'):
            i.set_second('dummy')

        i.set_state('LUNCH')
        i.set_second('test second lunch')
        assert i.lunch.p2 == 'test second lunch'

        i.set_state('DINNER')
        i.set_second('test second dinner')
        assert i.dinner.p2 == 'test second dinner'

        i.set_second('')
        assert i.dinner.p2 == 'test second dinner'

    def test_to_dict(self, init):
        assert init

        assert self.i01.to_dict() == {'lunch': Meal(), 'dinner': Meal()}
        assert self.i02.to_dict() == {'lunch': Meal(), 'dinner': Meal()}
        assert self.i03.to_dict() == {'lunch': Meal(), 'dinner': Meal()}
        assert self.i04.to_dict() == {'lunch': Meal(), 'dinner': Meal()}
        assert self.i05.to_dict() == {'lunch': Meal(), 'dinner': self.dinner}
        assert self.i06.to_dict() == {'lunch': Meal(), 'dinner': self.dinner}
        assert self.i07.to_dict() == {'lunch': Meal(), 'dinner': self.dinner}
        assert self.i08.to_dict() == {'lunch': Meal(), 'dinner': self.dinner}
        assert self.i09.to_dict() == {'lunch': self.lunch, 'dinner': Meal()}
        assert self.i10.to_dict() == {'lunch': self.lunch, 'dinner': Meal()}
        assert self.i11.to_dict() == {'lunch': self.lunch, 'dinner': Meal()}
        assert self.i12.to_dict() == {'lunch': self.lunch, 'dinner': Meal()}
        assert self.i13.to_dict() == {'lunch': self.lunch, 'dinner': self.dinner}
        assert self.i14.to_dict() == {'lunch': self.lunch, 'dinner': self.dinner}
        assert self.i15.to_dict() == {'lunch': self.lunch, 'dinner': self.dinner}
        assert self.i16.to_dict() == {'lunch': self.lunch, 'dinner': self.dinner}


class TestMeal:
    # noinspection PyAttributeOutsideInit
    @pytest.fixture
    def init(self):
        self.m1 = Meal(p1=None, p2=None)
        self.m2 = Meal(p1='meal_1', p2=None)
        self.m3 = Meal(p1=None, p2='meal_2')
        self.m4 = Meal(p1='meal_1', p2='meal_2')

        return True

    def test_is_emtpy(self, init):
        assert init

        assert self.m1.is_empty()
        assert not self.m2.is_empty()
        assert not self.m3.is_empty()
        assert not self.m4.is_empty()

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

        with pytest.raises(ValueError, match="Invalid arguments: {'foo': 'bar'}"):
            m1.update(foo='bar', p1='new_meal')


#

# class DailyMenu:
#     def __init__(self, day: int, month: int, year: int): ...
#     def __str__(self): ...
#     def __repr__(self): ...
#     def from_datetime(cls, dt): ...
#     def format_date(self): ...
#     def update(self, **kwargs): ...

class TestDailyMenu:

    def test_e_to_s(self):
        test = DailyMenu.e_to_s
        assert test('12 february 2016 tuesday') == '12 febrero 2016 martes'
        assert test('16 january friday') == '16 enero viernes'
        assert test('16 january friday') == '16 enero viernes'
        assert test('día: 25 de february de 2019 (monday)') == 'día: 25 de febrero de 2019 (lunes)'
        assert test('13 de december de 2016 (tuesday)') == '13 de diciembre de 2016 (martes)'
        assert test('13 de january de 2017 (friday)') == '13 de enero de 2017 (viernes)'
        assert test('23 de february de 2017 (thursday)') == '23 de febrero de 2017 (jueves)'
        assert test('6 de march de 2017 (monday)') == '6 de marzo de 2017 (lunes)'
        assert test('9 de april de 2017 (sunday)') == '9 de abril de 2017 (domingo)'
        assert test('30 de may de 2017 (tuesday)') == '30 de mayo de 2017 (martes)'
        assert test('28 de june de 2017 (wednesday)') == '28 de junio de 2017 (miércoles)'
        assert test('14 de july de 2017 (friday)') == '14 de julio de 2017 (viernes)'
        assert test('15 de august de 2017 (tuesday)') == '15 de agosto de 2017 (martes)'
        assert test('22 de september de 2017 (friday)') == '22 de septiembre de 2017 (viernes)'
        assert test('16 de october de 2017 (monday)') == '16 de octubre de 2017 (lunes)'
        assert test('7 de november de 2017 (tuesday)') == '7 de noviembre de 2017 (martes)'
        assert test('13 de december de 2017 (wednesday)') == '13 de diciembre de 2017 (miércoles)'

    def test_s_to_e(self):
        test = DailyMenu.s_to_e
        assert test('12 febrero 2016 martes') == '12 february 2016 tuesday'
        assert test('16 enero viernes') == '16 january friday'
        assert test('16 enero viernes') == '16 january friday'
        assert test('día: 25 de febrero de 2019 (lunes)') == 'día: 25 de february de 2019 (monday)'
        assert test('13 de diciembre de 2016 (martes)') == '13 de december de 2016 (tuesday)'
        assert test('13 de enero de 2017 (viernes)') == '13 de january de 2017 (friday)'
        assert test('23 de febrero de 2017 (jueves)') == '23 de february de 2017 (thursday)'
        assert test('6 de marzo de 2017 (lunes)') == '6 de march de 2017 (monday)'
        assert test('9 de abril de 2017 (domingo)') == '9 de april de 2017 (sunday)'
        assert test('30 de mayo de 2017 (martes)') == '30 de may de 2017 (tuesday)'
        assert test('28 de junio de 2017 (miércoles)') == '28 de june de 2017 (wednesday)'
        assert test('14 de julio de 2017 (viernes)') == '14 de july de 2017 (friday)'
        assert test('15 de agosto de 2017 (martes)') == '15 de august de 2017 (tuesday)'
        assert test('22 de septiembre de 2017 (viernes)') == '22 de september de 2017 (friday)'
        assert test('16 de octubre de 2017 (lunes)') == '16 de october de 2017 (monday)'
        assert test('7 de noviembre de 2017 (martes)') == '7 de november de 2017 (tuesday)'
        assert test('13 de diciembre de 2017 (miércoles)') == '13 de december de 2017 (wednesday)'

    # noinspection PyAttributeOutsideInit
    @pytest.fixture
    def init(self):
        dm = DailyMenu
        self.dm1 = dm(1, 1, 2019, lunch=Meal(), dinner=Meal())
        self.dm2 = dm(2, 1, 2019, lunch=Meal(), dinner=Meal(p1='D1'))
        self.dm3 = dm(4, 1, 2019, lunch=Meal(), dinner=Meal(p1='D1', p2='D2'))
        self.dm4 = dm(5, 1, 2019, lunch=Meal(p1='L1'), dinner=Meal())
        self.dm5 = dm(6, 1, 2019, lunch=Meal(p1='L1'), dinner=Meal(p1='D1'))
        self.dm6 = dm(8, 1, 2019, lunch=Meal(p1='L1'), dinner=Meal(p1='D1', p2='D2'))
        self.dm7 = dm(9, 1, 2019, lunch=Meal(p1='L1', p2='L2'), dinner=Meal())
        self.dm8 = dm(9, 1, 2019, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1'))
        self.dm9 = dm(9, 1, 2019, lunch=Meal(p1='L1', p2='L2'), dinner=Meal(p1='D1', p2='D2'))

        return True

    def test_to_string(self, init):
        assert init

        assert self.dm1.to_string() == '01 de enero de 2019 (martes)\n'
        assert self.dm2.to_string() == '02 de enero de 2019 (miércoles)\n - Cena\n   - D1\n'
        assert self.dm3.to_string() == '04 de enero de 2019 (viernes)\n - Cena\n   - D1\n   - D2\n'
        assert self.dm4.to_string() == '05 de enero de 2019 (sábado)\n - Comida\n   - L1\n'
        assert self.dm5.to_string() == '06 de enero de 2019 (domingo)\n - Comida\n   - L1\n - Cena\n   - D1\n'
        assert self.dm6.to_string() == '08 de enero de 2019 (martes)\n - Comida\n   - L1\n - Cena\n   - D1\n   - D2\n'
        assert self.dm7.to_string() == '09 de enero de 2019 (miércoles)\n - Comida\n   - L1\n   - L2\n'
        assert self.dm8.to_string() == '09 de enero de 2019 (miércoles)\n - Comida\n   - L1\n   - L2\n - Cena\n   - D1\n'
        assert self.dm9.to_string() == '09 de enero de 2019 (miércoles)\n - Comida\n   - L1\n   - L2\n - Cena\n   - D1\n   - D2\n'

    def test_to_html(self, init):
        assert init

        assert self.dm1.to_html() == '01 de enero de 2019 (martes)<br>'
        assert self.dm2.to_html() == '02 de enero de 2019 (miércoles)<br> - Cena<br>   - D1<br>'
        assert self.dm3.to_html() == '04 de enero de 2019 (viernes)<br> - Cena<br>   - D1<br>   - D2<br>'
        assert self.dm4.to_html() == '05 de enero de 2019 (sábado)<br> - Comida<br>   - L1<br>'
        assert self.dm5.to_html() == '06 de enero de 2019 (domingo)<br> - Comida<br>   - L1<br> - Cena<br>   - D1<br>'
        assert self.dm6.to_html() == '08 de enero de 2019 (martes)<br> - Comida<br>   - L1<br> - Cena<br>   - D1<br>   - D2<br>'
        assert self.dm7.to_html() == '09 de enero de 2019 (miércoles)<br> - Comida<br>   - L1<br>   - L2<br>'
        assert self.dm8.to_html() == '09 de enero de 2019 (miércoles)<br> - Comida<br>   - L1<br>   - L2<br> - Cena<br>   - D1<br>'
        assert self.dm9.to_html() == '09 de enero de 2019 (miércoles)<br> - Comida<br>   - L1<br>   - L2<br> - Cena<br>   - D1<br>   - D2<br>'

    def test_from_datetime(self):
        fdt = DailyMenu.from_datetime

        assert fdt('Día: 13 de diciembre de 2016 (martes)').date == datetime.date(2016, 12, 13)
        assert fdt('Día: 13 de enero de 2017 (viernes)').date == datetime.date(2017, 1, 13)
        assert fdt('Día: 23 de febrero de 2017 (jueves)').date == datetime.date(2017, 2, 23)
        assert fdt('Día: 6 de marzo de 2017 (lunes)').date == datetime.date(2017, 3, 6)
        assert fdt('Día: 9 de abril de 2017 (domingo)').date == datetime.date(2017, 4, 9)
        assert fdt('Día: 30 de mayo de 2017 (martes)').date == datetime.date(2017, 5, 30)
        assert fdt('Día: 28 de junio de 2017 (miércoles)').date == datetime.date(2017, 6, 28)
        assert fdt('Día: 14 de julio de 2017 (viernes)').date == datetime.date(2017, 7, 14)
        assert fdt('Día: 15 de agosto de 2017 (martes)').date == datetime.date(2017, 8, 15)
        assert fdt('Día: 22 de septiembre de 2017 (viernes)').date == datetime.date(2017, 9, 22)
        assert fdt('Día: 16 de octubre de 2017 (lunes)').date == datetime.date(2017, 10, 16)
        assert fdt('Día: 7 de noviembre de 2017 (martes)').date == datetime.date(2017, 11, 7)
        assert fdt('Día: 13 de diciembre de 2017 (miércoles)').date == datetime.date(2017, 12, 13)

        assert fdt(datetime.date(2016, 12, 13)).date == datetime.date(2016, 12, 13)
        assert fdt(datetime.date(2017, 1, 13)).date == datetime.date(2017, 1, 13)
        assert fdt(datetime.date(2017, 2, 23)).date == datetime.date(2017, 2, 23)
        assert fdt(datetime.date(2017, 3, 6)).date == datetime.date(2017, 3, 6)
        assert fdt(datetime.date(2017, 4, 9)).date == datetime.date(2017, 4, 9)
        assert fdt(datetime.date(2017, 5, 30)).date == datetime.date(2017, 5, 30)
        assert fdt(datetime.date(2017, 6, 28)).date == datetime.date(2017, 6, 28)
        assert fdt(datetime.date(2017, 7, 14)).date == datetime.date(2017, 7, 14)
        assert fdt(datetime.date(2017, 8, 15)).date == datetime.date(2017, 8, 15)
        assert fdt(datetime.date(2017, 9, 22)).date == datetime.date(2017, 9, 22)
        assert fdt(datetime.date(2017, 10, 16)).date == datetime.date(2017, 10, 16)
        assert fdt(datetime.date(2017, 11, 7)).date == datetime.date(2017, 11, 7)
        assert fdt(datetime.date(2017, 12, 13)).date == datetime.date(2017, 12, 13)

    def test_format_date(self):
        fdt = DailyMenu.from_datetime

        assert fdt(datetime.date(2016, 12, 13)).format_date() == '13 de diciembre de 2016 (martes)'
        assert fdt(datetime.date(2017, 1, 13)).format_date() == '13 de enero de 2017 (viernes)'
        assert fdt(datetime.date(2017, 2, 23)).format_date() == '23 de febrero de 2017 (jueves)'
        assert fdt(datetime.date(2017, 3, 6)).format_date() == '06 de marzo de 2017 (lunes)'
        assert fdt(datetime.date(2017, 4, 9)).format_date() == '09 de abril de 2017 (domingo)'
        assert fdt(datetime.date(2017, 5, 30)).format_date() == '30 de mayo de 2017 (martes)'
        assert fdt(datetime.date(2017, 6, 28)).format_date() == '28 de junio de 2017 (miércoles)'
        assert fdt(datetime.date(2017, 7, 14)).format_date() == '14 de julio de 2017 (viernes)'
        assert fdt(datetime.date(2017, 8, 15)).format_date() == '15 de agosto de 2017 (martes)'
        assert fdt(datetime.date(2017, 9, 22)).format_date() == '22 de septiembre de 2017 (viernes)'
        assert fdt(datetime.date(2017, 10, 16)).format_date() == '16 de octubre de 2017 (lunes)'
        assert fdt(datetime.date(2017, 11, 7)).format_date() == '07 de noviembre de 2017 (martes)'
        assert fdt(
            datetime.date(2017, 12, 13)).format_date() == '13 de diciembre de 2017 (miércoles)'

    def test_update(self):
        pass
