from rest_framework.test import APITestCase
from rest_framework.validators import ValidationError
from rest_framework import status

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask

from datetime import timedelta, datetime, date

from habits.handlers import HandleInterval, HandleTimeToDo, HandleTimeToDone
from habits.validators import (ValidateInterval,
                               ValidateDateTwoPart,
                               ValidateDateDay,
                               ValidateDateMinute,
                               ValidatorOneValueInput,
                               ValidatorNiceHabit,
                               ValidatorRalatedHabit,
                               ValidatorRelatedHabitSomePublished,
                               )
from habits.models import Habit
from habits.services import construct_periodic, construct_time_to_task


class TestHandlersHabits(TestCase):
    """Проверка обработчиков
    """    
    
    def test_handle_interval(self):
        """Проверка обработки строки в интервале
        """        
        result_days = HandleInterval.get_interval('30/0/0')
        result_hours = HandleInterval.get_interval('0/23/0')
        result_minutes = HandleInterval.get_interval('0/0/59')

        self.assertEqual(result_days, IntervalSchedule.objects.get(every=30, period='days'))
        self.assertEqual(result_hours, IntervalSchedule.objects.get(every=23, period='hours'))
        self.assertEqual(result_minutes, IntervalSchedule.objects.get(every=59, period='minutes'))
    
    def test_interval_exists_in_db(self):
        """Тест интервала автоматического создание интервала в БД
        """
        empty_db = IntervalSchedule.objects.get_queryset().exists()
        HandleInterval.get_interval('30/0/0')
        exists_item_db = IntervalSchedule.objects.get_queryset().exists()
        
        self.assertFalse(empty_db)
        self.assertTrue(exists_item_db)
        
    def test_interval_query(self):
        """Тест интервала вывода объекта если он существует в БД
        """
        # Создание элемента в БД теперь один элемент
        HandleInterval.get_interval('30/0/0')
        first_query = IntervalSchedule.objects.count()
        
        # Следуйщий запрос не создает элемент а вытаскивает
        # потому что он уже существует
        HandleInterval.get_interval('30/0/0')
        second_query = IntervalSchedule.objects.count()
        
        self.assertEqual(first_query, 1)
        self.assertEqual(first_query, second_query)
        
    def test_intervar_default(self):
        """Тест интервала дефолтного значение в случае пустого аргумента
        """
        result = HandleInterval.get_interval(None)
        
        self.assertEqual(result.every, 1)
        self.assertEqual(result.period, 'days')
        
    def test_intervar_duck_argument(self):
        """Тест не верного аргумента
        """
        with self.assertRaises(TypeError):
            HandleInterval.get_interval([1, 2, 3])
            
    def test_interval_duck_interval(self):
        """Тест не верного значения интервала
        """
        with self.assertRaises(ValueError):
            HandleInterval.get_interval('0/0/0/0')
        with self.assertRaises(ValueError):
            HandleInterval.get_interval('0/0/')
            
    def test_interval_with_validator(self):
        """Тест интервала с валидатором
        """
        # Каждые 20 часов
        value = {'interval': '0/20/0'}
        # Валидирование данных
        validator = ValidateInterval('interval')
        validator(value)
        # Получение валидных данных обработчику
        result = HandleInterval.get_interval(value['interval'])
        
        self.assertEqual((result.every, result.period), (20, 'hours'))
        
    def test_time_to_do(self):
        """Тест проверки времени действия
        """        
        time = '12:20'
        result = HandleTimeToDo.get_crontab_time(time)
        
        self.assertEqual(result, CrontabSchedule.objects.get(hour=12, minute=20))
        
    def test_time_to_do_save_to_db(self):
        """Тест проверки времени действия, сохранение объекта Crontab в БД
        """
        empty_db = CrontabSchedule.objects.get_queryset().exists()
        HandleTimeToDo.get_crontab_time('23:30')
        exists_item_db = CrontabSchedule.objects.get_queryset().exists()
        
        self.assertFalse(empty_db)
        self.assertTrue(exists_item_db)
        
    def test_time_to_do_query(self):
        """Тест времени действия, вывод объекта если он существует в БД
        """
        # Создание элемента в БД теперь один элемент
        HandleTimeToDo.get_crontab_time('1:15')
        first_query = CrontabSchedule.objects.count()
        
        # Следуйщий запрос не создает элемент а вытаскивает
        # потому что он уже существует
        HandleTimeToDo.get_crontab_time('1:15')
        second_query = CrontabSchedule.objects.count()
        
        self.assertEqual(first_query, 1)
        self.assertEqual(first_query, second_query)
        
    def test_time_to_do_duck_argument(self):
        """Тест не верного аргумента
        """
        with self.assertRaises(TypeError):
            HandleTimeToDo.get_crontab_time([1, 2, 3])
            
    def test_time_to_do_duck_time(self):
        """Тест не верного значения времени
        """
        with self.assertRaises(ValueError):
            HandleInterval.get_interval(':00')
        with self.assertRaises(ValueError):
            HandleInterval.get_interval('00:00:00')
            
    def test_time_to_do_with_validator(self):
        """Тест времени действия с валидатором
        """
        value = {'date': '9:12'}
        # Валидирование данных
        validator = ValidateDateDay('date')
        validator(value)
        # Получение валидных данных обработчику
        result = HandleTimeToDo.get_crontab_time(value['date'])
        
        self.assertEqual((result.hour, result.minute), (9, 12))
        
    def test_time_to_done(self):
        """Тест проверки времени
        """
        value = '1:49'
        result = HandleTimeToDone.get_time(value)
        
        self.assertEqual(result, timedelta(minutes=1, seconds=49))
        
    def test_time_to_done_duck_argument(self):
        """Тест не верного аргумента
        """
        with self.assertRaises(TypeError):
            HandleTimeToDone.get_time([1, 2, 3])
            
    def test_time_to_done_duck_time(self):
        """Тест не верного значения времени
        """
        with self.assertRaises(ValueError):
            HandleTimeToDone.get_time(':00')
        with self.assertRaises(ValueError):
            HandleTimeToDone.get_time('00:00:00')
            
    def test_time_to_done_with_validator(self):
        """Тест времени действия с валидатором
        """
        value = {'date': '0:59'}
        # Валидирование данных
        validator = ValidateDateMinute('date')
        validator(value)
        # Получение валидных данных обработчику
        result = HandleTimeToDone.get_time(value['date'])
        
        self.assertEqual((result.seconds), 59)
        

class TestValidatorsHabits(TestCase):
    """Тесты валидаторов
    """
    
    def test_interval_validator_duck_interval(self):
        """Тест валидатора интервала на множественное значение
        """        
        value = {'interval': '7/20/0'}
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], 'В интервале нельзя указывать одновременно день или час или минуты')
            
    def test_interval_validator_empty_value(self):
        """Тест валидатора интервала на пустое значение
        """
        value = {'interval': '0/0/0'}
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], 'Указанный интервал не может быть пустым, нужно указать одно из значений')
    
        
    def test_interval_validator_space_in_value(self):
        """Тест валидатора интервала на пробел в значении
        """
        value = {'interval': '0/ 10/0'}
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], '0/ 10/0 имеет пробелы, это не допустимо')
    
    def test_interval_validator_duck_interval_instance(self):
        """Тест валидатора на не правильный интервал
        """
        value1 = {'interval': '0/10/0/0'}
        value2 = {'interval': '0/10/'}
        value3 = {'interval': '0/10/b'}
        value4 = {'interval': []}
        
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value1)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], '0/10/0/0 должен быть интервалом по типу "7/0/0" что значит интервал из 7 дней')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value2)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], '0/10/ должен быть интервалом по типу "7/0/0" что значит интервал из 7 дней')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value3)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], '0/10/b должен быть интервалом по типу "7/0/0" что значит интервал из 7 дней')
            
        with self.assertRaises(ValidationError) as ex:
            validator(value4)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], '[] должен быть строкой')
            
    def test_interval_duck_value_interval(self):
        """Тест валидатора на не коректные значения в интервале
        """        
        value1 = {'interval': '-1/0/0'}
        value2 = {'interval': '0/61/0'}
        value3 = {'interval': '0/0/-60'}
        value4 = {'interval': '8/0/0'}
        
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value1)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], 'Значение day может быть больше или равно нулю, либо не более чем 7')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value2)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], 'Значение hour не может быть меньше 0 или больше чем 59')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value3)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], 'Значение minute не может быть меньше 0 или больше чем 59')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value4)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['interval'], 'Значение day может быть больше или равно нулю, либо не более чем 7')
            
    def test_interval_validator_entry_type(self):
        """Тест валидатора интервала на входящее имя поля
        """
        with self.assertRaises(TypeError):
            ValidateInterval([])
            
        with self.assertRaises(TypeError):
            ValidateInterval(1)
            
    def test_interval_validator_pass_test(self):
        """Тест валидатора интервала на валидные данные
        """
        value = {'interval': '0/10/0'}
        
        validator = ValidateInterval('interval')
        
        self.assertEqual(validator(value), None)
            
    def test_two_part_validator_entry_type(self):
        """Тест валидатора двух частей на входящее имя поля
        """
        with self.assertRaises(TypeError):
            ValidateDateTwoPart([])
            
        with self.assertRaises(TypeError):
            ValidateDateTwoPart(1)
            
    def test_two_part_validator_space_in_value(self):
        """Тест валидатора двух частей на пробел в значении
        """
        value ='10:0 0'
        
        with self.assertRaises(ValidationError) as ex:
            ValidateDateTwoPart(value)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['10:0 0'], '10:0 0 имеет пробелы, это не допустимо')
    
    def test_two_part_validator_duck_value(self):
        """Тест валидатора двух частей на плохие значения
        """
        value1 = '0/10/0'
        value2 = '0:10:0'
        value3 = ':0'
        value4 = ':'
        value5 = 'dd:00'
        
        with self.assertRaises(ValidationError) as ex:
            ValidateDateTwoPart(value1)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['0/10/0'], '0/10/0 не является корректным для данного поля, необходимо использовать разделитель ":" и стандартный вид должен быть: "18:30"')
            
        with self.assertRaises(ValidationError) as ex:
            ValidateDateTwoPart(value2)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['0:10:0'], '0:10:0 не является корректным для данного поля, необходимо использовать разделитель ":" и стандартный вид должен быть: "18:30"')
            
        with self.assertRaises(ValidationError) as ex:
            ValidateDateTwoPart(value3)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0][':0'], 'Значения в времени могут быть только циферными')
            
        with self.assertRaises(ValidationError) as ex:
            ValidateDateTwoPart(value4)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0][':'], 'Значения в времени могут быть только циферными')
            
        with self.assertRaises(ValidationError) as ex:
            ValidateDateTwoPart(value5)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['dd:00'], 'Значения в времени могут быть только циферными')
      
    def test_two_part_validator_pass_test(self):
        """Тест валидатора двух частей на валидность данных
        """
        value = '8:30'
        result = ValidateDateTwoPart(value)
        
        self.assertEqual(result.checked_values, (8, 30))
    
    def test_date_day_validator_entry_type(self):
        """Тест валидатора даты дня на входящее поле
        """        
        with self.assertRaises(TypeError):
            ValidateDateDay([])
            
        with self.assertRaises(TypeError):
            ValidateDateDay(1)
    
    def test_date_day_validator_duck_values(self):
        """Тест валидатора даты дня на плохие аргументы во времени
        """
        value1 = {'date': '24:00'}
        value2 = {'date': '-1:00'}
        value3 = {'date': '00:60'}
        value4 = {'date': '00:dd'}
        
        validator = ValidateDateDay('date')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value1)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['date'], 'Значение hour не может быть меньше 0 или больше 23')
            
        with self.assertRaises(ValidationError) as ex:
            validator(value2)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['date'], 'Значение hour не может быть меньше 0 или больше 23')
            
        with self.assertRaises(ValidationError) as ex:
            validator(value3)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['date'], 'Значение minute не может быть меньше 0 или больше 59')
            
        with self.assertRaises(ValidationError) as ex:
            validator(value4)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['00:dd'], 'Значения в времени могут быть только циферными')
            
    def test_date_day_validator_pass_test(self):
        """Тест валидатора даты дня на валидность данных
        """
        value = {'date': '20:45'}
        validator = ValidateDateDay('date')
        result = validator(value)
        
        self.assertEqual(result, None)
        
    def test_date_minute_validator_entry_type(self):
        """Тест валидатора даты минут на входящее поле
        """        
        with self.assertRaises(TypeError):
            ValidateDateMinute([])
            
        with self.assertRaises(TypeError):
            ValidateDateMinute(1)
    
    def test_date_minute_validator_duck_values(self):
        """Тест валидатора даты минут на плохие аргументы во времени
        """
        value1 = {'date': '2:01'}
        value2 = {'date': '-1:00'}
        value3 = {'date': '1:60'}
        value4 = {'date': '00:dd'}
        
        validator = ValidateDateMinute('date')
        
        with self.assertRaises(ValidationError) as ex:
            validator(value1)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['date'], 'Было полученно более двух минут!')
            
        with self.assertRaises(ValidationError) as ex:
            validator(value2)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['date'], 'Значение minute не корректное')
            
        with self.assertRaises(ValidationError) as ex:
            validator(value3)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['date'], 'Значение second не корректное')
            
        with self.assertRaises(ValidationError) as ex:
            validator(value4)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['00:dd'], 'Значения в времени могут быть только циферными')
            
    def test_date_minute_validator_pass_test(self):
        """Тест валидатора даты минут на валидность данных
        """
        value = {'date': '1:45'}
        validator = ValidateDateMinute('date')
        result = validator(value)
        
        self.assertEqual(result, None)
        
    def test_validator_one_value_input(self):
        """Проверка валидатора для выбора только одного поля
        """
        # Проверка на число    
        with self.assertRaises(TypeError):
            ValidatorOneValueInput(223)
        
        # Проверка на список с числом  
        with self.assertRaises(TypeError):
            ValidatorOneValueInput(['str', 223])
            
        # Проверка списка < 2
        with self.assertRaises(KeyError):
            ValidatorOneValueInput(['str',])
            
        # Проверка списка > 2
        with self.assertRaises(KeyError):
            ValidatorOneValueInput(['str', 'str', 'str'])

        validate = ValidatorOneValueInput(['first', 'second'])
        # Проверка корректности заполнения
        self.assertEqual(validate.fields, ['first', 'second'])
        # Проверка корректности проверки правильных аргументов
        self.assertIsNone(validate({'second': 1}))
        
    def test_nice_habit_validator_entry_type(self):
        """Тест валидатора приятной привычки на входящее поле
        """        
        with self.assertRaises(TypeError):
            ValidatorNiceHabit('some', 1)
            
        with self.assertRaises(TypeError):
            ValidatorNiceHabit(1)
        
        with self.assertRaises(ValueError):
            ValidatorNiceHabit([], [])
            
        with self.assertRaises(ValueError):
            ValidatorNiceHabit('some', ['some', 'some'])
            
        with self.assertRaises(ValueError):
            ValidatorNiceHabit('some', ['first', 'second', 'third'])
    
    def test_nice_habit_pass_test(self):
        """Тест валидатора прияной привычки при валидных данных
        """
        data = {
            'nice_habbit': True,
            'reward' : None,
            'related_habit': None,
        }
        validator = ValidatorNiceHabit('nice_habbit', ['nice_habbit', 'reward', 'related_habit'])
        result = validator(data)
        self.assertEqual(result, None)
        
    def test_not_nice_habit(self):
        """Тест валидатора если привычка не является приятной
        """
        data = {
            'nice_habbit': False,
            'reward' : 'reward',
            'related_habit': None,
        }      
        validator = ValidatorNiceHabit('nice_habbit', ['nice_habbit', 'reward', 'related_habit'])
        result = validator(data)
        self.assertEqual(result, None)
        
    def test_nice_habit_duck_data(self):
        """Тест валидатора приятной привычки на не валидные данные
        """
        data = {
            'nice_habbit': True,
            'reward' : 'reward',
            'related_habit': None,
        }      
        validator = ValidatorNiceHabit('nice_habbit', ['nice_habbit', 'reward', 'related_habit'])
        
        with self.assertRaises(ValidationError) as ex:
            validator(data)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['nice_habbit'], 'При указании приятной привычки награду и связаную привычку указывать нельзя')
    
    def test_nice_habit_duck_data_2(self):
        """Тест валидатора приятной привычки на не валидные данные
        """
        data = {
            'nice_habbit': True,
            'reward' : None,
            'related_habit': 'Have',
        }      
        validator = ValidatorNiceHabit('nice_habbit', ['nice_habbit', 'reward', 'related_habit'])
        with self.assertRaises(ValidationError) as ex:
            validator(data)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['nice_habbit'], 'При указании приятной привычки награду и связаную привычку указывать нельзя')
            
    def test_related_habit_nice(self):
        """Проверка валидатора на вхождение плохих аргументов
        """        
        with self.assertRaises(TypeError):
            ValidatorRalatedHabit([])
            
        with self.assertRaises(TypeError):
            ValidatorRalatedHabit(1)
        
    def test_related_habit_nice_pass_test(self):
        """Проверка валидатора если значение верное
        """
        user = get_user_model().objects.create_user('user',
                                                         'user@gmail.com',
                                                         'usertestuser',
                                                         )
        cron = CrontabSchedule.objects.create(hour=18, minute=41)
        interval = IntervalSchedule.objects.create(every=1, period='days')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     )
        data = {
            'ralated_habit': habit,
        }
        validator = ValidatorRalatedHabit('ralated_habit')
        result = validator(data)
        
        self.assertEqual(result, None)
        
    def test_retaled_habit_duck_value(self):
        """Проверка валидатора если значение не верное
        """
        user = get_user_model().objects.create_user('user',
                                                         'user@gmail.com',
                                                         'usertestuser',
                                                         )
        cron = CrontabSchedule.objects.create(hour=18, minute=41)
        interval = IntervalSchedule.objects.create(every=1, period='days')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=interval,
                                     reward='reward',
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     )
        data = {
            'related_habit': habit,
        }
        validator = ValidatorRalatedHabit('related_habit')
        
        with self.assertRaises(ValidationError) as ex:
            validator(data)
        the_exception = ex.exception
        self.assertEqual(the_exception.args[0]['related_habit'], 'Связаная привычка может быть только приятной')
        
        
class TestAPIHabit(APITestCase):
    """Тесты API привычек
    """
    
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user('user',
                                                         'user@gmail.com',
                                                         'usertestuser',
                                                         )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('habits:habit_create')
        self.cron = CrontabSchedule.objects.create(hour=18, minute=41)
        self.interval = IntervalSchedule.objects.create(every=1, period='days')
        
    def test_create_habit(self):
        """Тест создания привычки
        """
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'periodic': '2/0/0',
            'reward': 'test_reward',
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"place": "test_place",
                                        "time_to_do": "18:41",
                                        "action": "test_action",
                                        "is_nice_habit": False,
                                        "related_habit": None,
                                        "periodic": "every 2 days",
                                        "reward": "test_reward",
                                        "time_to_done": "0:01:32",
                                        })
        self.assertEqual(PeriodicTask.objects.count(), 1)

    def test_create_habit_bad_request_input_two_values(self):
        """Тест проверки вхождения двух полей которые не могут быть вместе
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': 'test_reward',
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['error'][0]), 'related_habit и reward не могут быть определенны вместе')
        self.assertEqual(PeriodicTask.objects.count(), 0)
        
    def test_create_habit_bad_request_related_habbit_is_not_nice(self):
        """Тест проверки вхождения связанной модели с полезной привычкой
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     reward='reward',
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': None,
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['related_habit'][0]), 'Связаная привычка может быть только приятной')
        
    def test_create_habit_bad_request_nice_habit(self):
        """Тест проверки приятной привычки с неправильными аргументами
        """        
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': True,
            'periodic': '2/0/0',
            'reward': 'reward',
            'time_to_done': '1:32',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['is_nice_habit'][0]), 'При указании приятной привычки награду и связаную привычку указывать нельзя')
        self.assertEqual(PeriodicTask.objects.count(), 0)

    def test_create_habit_bad_request_related_habbit_is_some_publish(self):
        """Тест проверки вхождения связанной модели не с одинаковой публичностью
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=False,
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': None,
            'time_to_done': '1:32',
            'is_published': True,
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['related_habit'][0]), 'Связанная привычка и текущая не могут иметь разные статусы публичности')
        
    def test_create_habit_with_related_habit(self):
        """Тест проверки вхождения связанной модели с одинаковой публичностью
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=False,
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': habit.pk,
            'periodic': '2/0/0',
            'reward': None,
            'time_to_done': '1:32',
            'is_published': False,
        }
        response = self.client.post(self.url, data, format='json')
        count_in_bd = Habit.objects.count()
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(count_in_bd, 2)
    
    def test_retrieve_habit_private(self):
        """Тест отказа в просмотре приватной привычки
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     reward=None,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=False,
                                     )
        url = reverse('habits:habit_retrieve', kwargs={'pk': habit.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_habit_bad_related_habit(self):
        """Тест привязки чужой привычки
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')    
        related = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'related_habit': related.pk,
            'periodic': '2/0/0',
            'time_to_done': '1:32',
            'is_published': True,
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_list_of_habits_personal(self):
        """Тест списка привычек связанных с пользователем
        """        
        url = reverse('habits:habit_list_private')
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')    
        Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        responce = self.client.get(url)
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data['count'], 1)
        
    def test_habit_retrieve_block_view(self):
        """Тест блокировки доступа к привычке не являющейся личной
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')    
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_retrieve', kwargs={'pk': habit.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(str(response.data), 'Данную привычку может просматривать только владелец')
        
    def test_list_of_habits_published(self):
        """Тест списка привычек связанных с пользователем
        """        
        url = reverse('habits:habit_list')
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        responce = self.client.get(url)
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data['count'], 2)
        
    def test_habit_update(self):
        """Тест обновления привычки
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_update', kwargs={'pk': habit.pk})
        data = {
            'place': 'update_place',
            'time_to_do': '20:30',
            'action': 'update_action',
            'periodic': '4/0/0',
            'reward': 'update_reward',
            'time_to_done': '0:59',
            'is_published': False,
        }
        responce = self.client.patch(url, data)
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data['place'], 'update_place')
        self.assertEqual(responce.data['time_to_done'], '0:00:59')
    
    def test_habit_update_change_raleted_published(self):
        """Тест изменения публичности у связанной привычки при изменении у основной
        """        
        ralated = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     related_habit=ralated,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        data_habit = {
            'is_published': False
        }
        
        url_habit = reverse('habits:habit_update', kwargs={'pk': habit.pk})
        
        responce_habit = self.client.patch(url_habit, data_habit)
        
        habit = Habit.objects.get(pk=habit.pk)
        ralated = Habit.objects.get(pk=ralated.pk)
        self.assertEqual(responce_habit.status_code, status.HTTP_200_OK)
        self.assertEqual(habit.is_published, False)
        self.assertEqual(ralated.is_published, False)
        
        data_ralated = {
            'is_published': True
        }
        
        url_ralated = reverse('habits:habit_update', kwargs={'pk': ralated.pk})
        
        responce_ralated = self.client.patch(url_ralated, data_ralated)
        habit = Habit.objects.get(pk=habit.pk)
        ralated = Habit.objects.get(pk=ralated.pk)
        self.assertEqual(responce_ralated.status_code, status.HTTP_200_OK)
        self.assertEqual(ralated.is_published, True)
        self.assertEqual(habit.is_published, True)
        
    def test_habit_update_block_permission(self):
        """Тест блокировки доступа к изменению привычки если не является владельцем
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_update', kwargs={'pk': habit.pk})
        data = {
            'place': 'update_place',
            'time_to_do': '20:30',
            'action': 'update_action',
            'periodic': '4/0/0',
            'reward': 'update_reward',
            'time_to_done': '0:59',
            'is_published': False,
        }
        responce = self.client.patch(url, data)
        
        self.assertEqual(responce.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_delete(self):
        """Тест удаления привычки
        """
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_delete', kwargs={'pk': habit.pk})
        responce = self.client.delete(url)
        
        self.assertEqual(responce.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_habit_delete_save_related(self):
        """Тест удаления основной и сохранение связанной
        """
        related = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=True,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     related_habit=related,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_delete', kwargs={'pk': related.pk})
        responce = self.client.delete(url)
        habit = Habit.objects.get(pk=habit.pk)
        
        self.assertEqual(responce.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(habit.related_habit, None)
        
    def test_habit_delete_block_permission(self):
        """Тест блокировки доступа к удалению привычки если не является владельцем
        """
        user = get_user_model().objects.create_user('owner', 'owner@gmail.com', 'ownerpass', phone='+7(900)9001000')
        habit = Habit.objects.create(owner=user,
                                     place='test_place',
                                     time_to_do=self.cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=self.interval,
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     is_published=True,
                                     )
        url = reverse('habits:habit_delete', kwargs={'pk': habit.pk})
        responce = self.client.delete(url)
        
        self.assertEqual(responce.status_code, status.HTTP_403_FORBIDDEN)


class TestPeriodicTask(APITestCase):
    """Тесты преодических задач
    """    
    def setUp(self):
        self.user = get_user_model().objects.create_user('owner',
                                                         'owner@gmail.com',
                                                         'ownerpass',
                                                         phone='+7(900)9001000',
                                                         tg_id=1000000,)
        self.client.force_authenticate(user=self.user)
        url = reverse('habits:habit_create')
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': False,
            'periodic': '2/0/0',
            'reward': 'test_reward',
            'time_to_done': '1:32',
        }
        self.client.post(url, data, format='json')
        self.habit = Habit.objects.get(place='test_place')
        self.task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')

    def test_created_periodic_task(self):
        """Тест созданной периодической задачи
        """    
        self.assertTrue(self.task.enabled)
        self.assertEqual(self.task.interval.every, 2)
        self.assertEqual(self.task.start_time.hour, 18)
        self.assertEqual(self.task.start_time.minute, 41)

    def test_update_periodic_task_two_arguments(self):
        """Тест обновления периодической задачи оба аргумента
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk}) 
        data = {
            'time_to_do': '11:22',
            'periodic': '0/12/0',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(task.interval.every, 12)
        self.assertEqual(task.start_time.hour, 11)
        self.assertEqual(task.start_time.minute, 22)
        
    def test_update_periodic_task_period_argument(self):
        """Тест обновления периодической задачи интервал аргумента
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk}) 
        data = {
            'periodic': '0/0/30',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(task.interval.every, 30)
        self.assertEqual(task.interval.period, 'minutes')
        
    def test_update_periodic_no_argument(self):
        """Тест обновления периодической задачи без аргументов времени
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk}) 
        data = {
            'place': 'test_place_update',
            'action': 'test_action_update',
            'reward': 'test_reward_update',
            'time_to_done': '0:11',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(self.task.interval.every, 2)
        self.assertEqual(self.task.start_time.hour, 18)
        self.assertEqual(self.task.start_time.minute, 41)
        
    def test_update_periodic_task_time_to_do_argument(self):
        """Тест обновления периодической задачи время выполнения аргумент
        """
        url = reverse('habits:habit_update', kwargs={'pk': self.habit.pk}) 
        data = {
            'time_to_do': '3:04',
        }
        response = self.client.patch(url, data, format='json')
        task = PeriodicTask.objects.get(name__contains=f'U-{self.user.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(task.enabled)
        self.assertEqual(task.start_time.hour, 3)
        self.assertEqual(task.start_time.minute, 4)

    def test_delete_periodic_task(self):
        """Тест удаления периодической задачи
        """
        url = reverse('habits:habit_delete', kwargs={'pk': self.habit.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)
        self.assertEqual(PeriodicTask.objects.count(), 0)
        
            
class TestTelegram(TestCase):
    """Тесты касающиеся телеграма
    """    
    
    def test_construct_petiodic(self):
        """Тест конструктора периодичности
        """
        self.assertEqual(construct_periodic(1, 'days'), 'Каждый день')
        self.assertEqual(construct_periodic(2, 'days'), 'Каждые 2 дня')
        self.assertEqual(construct_periodic(3, 'days'), 'Каждые 3 дня')
        self.assertEqual(construct_periodic(4, 'days'), 'Каждые 4 дня')
        self.assertEqual(construct_periodic(5, 'days'), 'Каждые 5 дней')
        self.assertEqual(construct_periodic(6, 'days'), 'Каждые 6 дней')
        self.assertEqual(construct_periodic(7, 'days'), 'Каждые 7 дней')
        self.assertEqual(construct_periodic(1, 'hours'), 'Каждый час')
        self.assertEqual(construct_periodic(2, 'hours'), 'Каждые 2 часа')
        self.assertEqual(construct_periodic(3, 'hours'), 'Каждые 3 часа')
        self.assertEqual(construct_periodic(4, 'hours'), 'Каждые 4 часа')
        self.assertEqual(construct_periodic(5, 'hours'), 'Каждые 5 часов')
        self.assertEqual(construct_periodic(6, 'hours'), 'Каждые 6 часов')
        self.assertEqual(construct_periodic(7, 'hours'), 'Каждые 7 часов')
        self.assertEqual(construct_periodic(8, 'hours'), 'Каждые 8 часов')
        self.assertEqual(construct_periodic(9, 'hours'), 'Каждые 9 часов')
        self.assertEqual(construct_periodic(10, 'hours'), 'Каждые 10 часов')
        self.assertEqual(construct_periodic(11, 'hours'), 'Каждые 11 часов')
        self.assertEqual(construct_periodic(12, 'hours'), 'Каждые 12 часов')
        self.assertEqual(construct_periodic(13, 'hours'), 'Каждые 13 часов')
        self.assertEqual(construct_periodic(14, 'hours'), 'Каждые 14 часов')
        self.assertEqual(construct_periodic(15, 'hours'), 'Каждые 15 часов')
        self.assertEqual(construct_periodic(16, 'hours'), 'Каждые 16 часов')
        self.assertEqual(construct_periodic(17, 'hours'), 'Каждые 17 часов')
        self.assertEqual(construct_periodic(18, 'hours'), 'Каждые 18 часов')
        self.assertEqual(construct_periodic(19, 'hours'), 'Каждые 19 часов')
        self.assertEqual(construct_periodic(20, 'hours'), 'Каждые 20 часов')
        self.assertEqual(construct_periodic(21, 'hours'), 'Каждый 21 час')
        self.assertEqual(construct_periodic(22, 'hours'), 'Каждые 22 часа')
        self.assertEqual(construct_periodic(23, 'hours'), 'Каждые 23 часа')
        self.assertEqual(construct_periodic(1, 'minutes'), 'Каждую минуту')
        self.assertEqual(construct_periodic(2, 'minutes'), 'Каждые 2 минуты')
        self.assertEqual(construct_periodic(3, 'minutes'), 'Каждые 3 минуты')
        self.assertEqual(construct_periodic(4, 'minutes'), 'Каждые 4 минуты')
        self.assertEqual(construct_periodic(5, 'minutes'), 'Каждые 5 минут')
        self.assertEqual(construct_periodic(6, 'minutes'), 'Каждые 6 минут')
        self.assertEqual(construct_periodic(7, 'minutes'), 'Каждые 7 минут')
        self.assertEqual(construct_periodic(8, 'minutes'), 'Каждые 8 минут')
        self.assertEqual(construct_periodic(9, 'minutes'), 'Каждые 9 минут')
        self.assertEqual(construct_periodic(10, 'minutes'), 'Каждые 10 минут')
        self.assertEqual(construct_periodic(11, 'minutes'), 'Каждые 11 минут')
        self.assertEqual(construct_periodic(12, 'minutes'), 'Каждые 12 минут')
        self.assertEqual(construct_periodic(13, 'minutes'), 'Каждые 13 минут')
        self.assertEqual(construct_periodic(14, 'minutes'), 'Каждые 14 минут')
        self.assertEqual(construct_periodic(15, 'minutes'), 'Каждые 15 минут')
        self.assertEqual(construct_periodic(16, 'minutes'), 'Каждые 16 минут')
        self.assertEqual(construct_periodic(17, 'minutes'), 'Каждые 17 минут')
        self.assertEqual(construct_periodic(18, 'minutes'), 'Каждые 18 минут')
        self.assertEqual(construct_periodic(19, 'minutes'), 'Каждые 19 минут')
        self.assertEqual(construct_periodic(20, 'minutes'), 'Каждые 20 минут')
        self.assertEqual(construct_periodic(21, 'minutes'), 'Каждую 21 минуту')
        self.assertEqual(construct_periodic(22, 'minutes'), 'Каждые 22 минуты')
        self.assertEqual(construct_periodic(23, 'minutes'), 'Каждые 23 минуты')
        self.assertEqual(construct_periodic(24, 'minutes'), 'Каждые 24 минуты')
        self.assertEqual(construct_periodic(25, 'minutes'), 'Каждые 25 минут')
        self.assertEqual(construct_periodic(26, 'minutes'), 'Каждые 26 минут')
        self.assertEqual(construct_periodic(27, 'minutes'), 'Каждые 27 минут')
        self.assertEqual(construct_periodic(28, 'minutes'), 'Каждые 28 минут')
        self.assertEqual(construct_periodic(29, 'minutes'), 'Каждые 29 минут')
        self.assertEqual(construct_periodic(30, 'minutes'), 'Каждые 30 минут')
        self.assertEqual(construct_periodic(31, 'minutes'), 'Каждую 31 минуту')
        self.assertEqual(construct_periodic(32, 'minutes'), 'Каждые 32 минуты')
        self.assertEqual(construct_periodic(33, 'minutes'), 'Каждые 33 минуты')
        self.assertEqual(construct_periodic(34, 'minutes'), 'Каждые 34 минуты')
        self.assertEqual(construct_periodic(35, 'minutes'), 'Каждые 35 минут')
        self.assertEqual(construct_periodic(36, 'minutes'), 'Каждые 36 минут')
        self.assertEqual(construct_periodic(37, 'minutes'), 'Каждые 37 минут')
        self.assertEqual(construct_periodic(38, 'minutes'), 'Каждые 38 минут')
        self.assertEqual(construct_periodic(39, 'minutes'), 'Каждые 39 минут')
        self.assertEqual(construct_periodic(40, 'minutes'), 'Каждые 40 минут')
        self.assertEqual(construct_periodic(41, 'minutes'), 'Каждую 41 минуту')
        self.assertEqual(construct_periodic(42, 'minutes'), 'Каждые 42 минуты')
        self.assertEqual(construct_periodic(43, 'minutes'), 'Каждые 43 минуты')
        self.assertEqual(construct_periodic(44, 'minutes'), 'Каждые 44 минуты')
        self.assertEqual(construct_periodic(45, 'minutes'), 'Каждые 45 минут')
        self.assertEqual(construct_periodic(46, 'minutes'), 'Каждые 46 минут')
        self.assertEqual(construct_periodic(47, 'minutes'), 'Каждые 47 минут')
        self.assertEqual(construct_periodic(48, 'minutes'), 'Каждые 48 минут')
        self.assertEqual(construct_periodic(49, 'minutes'), 'Каждые 49 минут')
        self.assertEqual(construct_periodic(50, 'minutes'), 'Каждые 50 минут')
        self.assertEqual(construct_periodic(51, 'minutes'), 'Каждую 51 минуту')
        self.assertEqual(construct_periodic(52, 'minutes'), 'Каждые 52 минуты')
        self.assertEqual(construct_periodic(53, 'minutes'), 'Каждые 53 минуты')
        self.assertEqual(construct_periodic(54, 'minutes'), 'Каждые 54 минуты')
        self.assertEqual(construct_periodic(55, 'minutes'), 'Каждые 55 минут')
        self.assertEqual(construct_periodic(56, 'minutes'), 'Каждые 56 минут')
        self.assertEqual(construct_periodic(57, 'minutes'), 'Каждые 57 минут')
        self.assertEqual(construct_periodic(58, 'minutes'), 'Каждые 58 минут')
        self.assertEqual(construct_periodic(59, 'minutes'), 'Каждые 59 минут')
        
    def test_construct_time(self):
        """Тест проверки переработки времени
        """
        cron = CrontabSchedule.objects.create(hour=18, minute=30)
        day_now = date.today()
        self.assertEqual(construct_time_to_task(time_interval=cron), datetime(year=day_now.year,
                                                                              month=day_now.month,
                                                                              day=day_now.day,
                                                                              hour=18,
                                                                              minute=30,
                                                                              tzinfo=timezone.get_current_timezone()
                                                                              ))
        
        