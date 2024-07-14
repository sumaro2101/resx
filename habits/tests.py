from rest_framework.test import APITestCase
from rest_framework.validators import ValidationError
from rest_framework import status

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from django_celery_beat.models import IntervalSchedule, CrontabSchedule

from datetime import timedelta

from habits.handlers import HandleInterval, HandleTimeToDo, HandleTimeToDone
from habits.validators import (ValidateInterval,
                               ValidateDateTwoPart,
                               ValidateDateDay,
                               ValidateDateMinute, ValidatorOneValueInput,
                               )
from habits.models import Habit


class TestHandlersHabits(TestCase):
    """Проверка обработчиков
    """    
    
    def test_handle_interval(self):
        """Проверка обработки строки в интервале
        """        
        result_days = HandleInterval.get_interval('30/0/0')
        result_hours = HandleInterval.get_interval('0/23/0')
        result_minutes = HandleInterval.get_interval('0/0/59')

        self.assertEqual(result_days, IntervalSchedule.objects.get(every=30, period='DAYS'))
        self.assertEqual(result_hours, IntervalSchedule.objects.get(every=23, period='HOURS'))
        self.assertEqual(result_minutes, IntervalSchedule.objects.get(every=59, period='MINUTES'))
    
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
        self.assertEqual(result.period, 'DAYS')
        
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
        
        self.assertEqual((result.every, result.period), (20, 'HOURS'))
        
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
        
        with self.assertRaises(ValidationError):
            validator(value)
            
    def test_interval_validator_empty_value(self):
        """Тест валидатора интервала на пустое значение
        """
        value = {'interval': '0/0/0'}
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError):
            validator(value)
        
    def test_interval_validator_space_in_value(self):
        """Тест валидатора интервала на пробел в значении
        """
        value = {'interval': '0/ 10/0'}
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError):
            validator(value)
    
    def test_interval_validator_duck_interval_instance(self):
        """Тест валидатора на не правильный интервал
        """
        value1 = {'interval': '0/10/0/0'}
        value2 = {'interval': '0/10/'}
        value3 = {'interval': '0/10/b'}
        value4 = {'interval': []}
        
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError):
            validator(value1)
        
        with self.assertRaises(ValidationError):
            validator(value2)
        
        with self.assertRaises(ValidationError):
            validator(value3)
            
        with self.assertRaises(ValidationError):
            validator(value4)
            
    def test_interval_duck_value_interval(self):
        """Тест валидатора на не коректные значения в интервале
        """        
        value1 = {'interval': '-1/0/0'}
        value2 = {'interval': '0/61/0'}
        value3 = {'interval': '0/0/-60'}
        value4 = {'interval': '8/0/0'}
        
        validator = ValidateInterval('interval')
        
        with self.assertRaises(ValidationError):
            validator(value1)
        
        with self.assertRaises(ValidationError):
            validator(value2)
        
        with self.assertRaises(ValidationError):
            validator(value3)
        
        with self.assertRaises(ValidationError):
            validator(value4)
            
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
        
        with self.assertRaises(ValidationError):
            ValidateDateTwoPart(value)
    
    def test_two_part_validator_duck_value(self):
        """Тест валидатора двух частей на плохие значения
        """
        value1 = '0/10/0'
        value2 = '0:10:0'
        value3 = ':0'
        value4 = ':'
        value5 = 'dd:00'
        
        with self.assertRaises(ValidationError):
            ValidateDateTwoPart(value1)
            
        with self.assertRaises(ValidationError):
            ValidateDateTwoPart(value2)
            
        with self.assertRaises(ValidationError):
            ValidateDateTwoPart(value3)
            
        with self.assertRaises(ValidationError):
            ValidateDateTwoPart(value4)
            
        with self.assertRaises(ValidationError):
            ValidateDateTwoPart(value5)
      
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
        
        with self.assertRaises(ValidationError):
            validator(value1)
            
        with self.assertRaises(ValidationError):
            validator(value2)
            
        with self.assertRaises(ValidationError):
            validator(value3)
            
        with self.assertRaises(ValidationError):
            validator(value4)
            
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
        
        with self.assertRaises(ValidationError):
            validator(value1)
            
        with self.assertRaises(ValidationError):
            validator(value2)
            
        with self.assertRaises(ValidationError):
            validator(value3)
            
        with self.assertRaises(ValidationError):
            validator(value4)
            
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
        
        
class TestAPIHabit(APITestCase):
    """Тесты API привычек
    """
    
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user('user',
                                                         'user@gmail.com',
                                                         'usertestuser',
                                                         )
        self.client.force_authenticate(user=self.user)
        
    def test_create_habit(self):
        """Тест создания привычки
        """
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
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"place": "test_place",
                                        "time_to_do": "41 18 * * * (m/h/dM/MY/d) UTC",
                                        "action": "test_action",
                                        "is_nice_habit": False,
                                        "related_habit": None,
                                        "periodic": "каждые 2 None",
                                        "reward": "test_reward",
                                        "time_to_done": "0:01:32",
                                        "is_published": False
                                        })

    def test_create_habit_bad_request_input_two_values(self):
        """Тест проверки выхождения двух полей которые не могут быть вместе
        """
        cron = CrontabSchedule.objects.create(hour=18, minute=41)
        interval = IntervalSchedule.objects.create(every=1, period='DAYS')
        habit = Habit.objects.create(owner=self.user,
                                     place='test_place',
                                     time_to_do=cron,
                                     action='test_actions',
                                     is_nice_habit=False,
                                     periodic=interval,
                                     reward='test_reward',
                                     time_to_done=timedelta(minutes=1, seconds=32),
                                     )
        url = reverse('habits:habit_create')
        data = {
            'place': 'test_place',
            'time_to_do': '18:41',
            'action': 'test_action',
            'is_nice_habit': True,
            'related_habit': 1,
            'periodic': '2/0/0',
            'reward': 'test_reward',
            'time_to_done': '1:32',
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        