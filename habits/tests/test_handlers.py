from django.test import TestCase

from django_celery_beat.models import CrontabSchedule

from datetime import timedelta

from habits.handlers import HandleInterval, HandleTimeToDo, HandleTimeToDone, HandleCronScheduleToTask
from habits.validators import (ValidateInterval,
                               ValidateDateDay,
                               ValidateDateMinute,

                               )


class TestHandlersHabits(TestCase):
    """Проверка обработчиков
    """    
    
    def test_handle_interval(self):
        """Проверка обработки строки в интервале
        """        
        result_days = HandleInterval.get_interval('30/0/0')
        result_hours = HandleInterval.get_interval('0/23/0')
        result_minutes = HandleInterval.get_interval('0/0/59')

        self.assertEqual(result_days, CrontabSchedule.objects.get(day_of_month='*/30'))
        self.assertEqual(result_hours, CrontabSchedule.objects.get(hour='*/23'))
        self.assertEqual(result_minutes, CrontabSchedule.objects.get(minute='*/59'))
    
    def test_interval_exists_in_db(self):
        """Тест интервала автоматического создание интервала в БД
        """
        empty_db = CrontabSchedule.objects.get_queryset().exists()
        HandleInterval.get_interval('30/0/0')
        exists_item_db = CrontabSchedule.objects.get_queryset().exists()
        
        self.assertFalse(empty_db)
        self.assertTrue(exists_item_db)
        
    def test_interval_query(self):
        """Тест интервала вывода объекта если он существует в БД
        """
        # Создание элемента в БД теперь один элемент
        HandleInterval.get_interval('30/0/0')
        first_query = CrontabSchedule.objects.count()
        
        # Следуйщий запрос не создает элемент а вытаскивает
        # потому что он уже существует
        HandleInterval.get_interval('30/0/0')
        second_query = CrontabSchedule.objects.count()
        
        self.assertEqual(first_query, 1)
        self.assertEqual(first_query, second_query)
        
    def test_intervar_default(self):
        """Тест интервала дефолтного значение в случае пустого аргумента
        """
        result = HandleInterval.get_interval(None)
        
        self.assertEqual(result.minute, '*')
        self.assertEqual(result.hour, '*')
        self.assertEqual(result.day_of_month, '*/1')
        
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
        
        self.assertEqual((result.minute, result.hour), ('*', '*/20'))
        
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
        
    def test_interval_to_task_all_arguments(self):
        """Тест обработчика для задачи
        """
        first = CrontabSchedule.objects.create(minute=30, hour=18)
        second = CrontabSchedule.objects.create(day_of_month='*/2')
        result = HandleCronScheduleToTask.get_interval_to_task(first, second)
        
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.hour, 18)
        self.assertEqual(result.day_of_month, '*/2')
        
    def test_interval_to_task_one_hour_argument(self):
        """Тест обработчика для задачи
        """
        first = CrontabSchedule.objects.create(minute=30, hour=18)
        second = CrontabSchedule.objects.create(hour='*/12')
        result = HandleCronScheduleToTask.get_interval_to_task(first, second)
        
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.hour, '*/12')
        
    def test_interval_to_task_one_minute_argument(self):
        """Тест обработчика для задачи
        """
        first = CrontabSchedule.objects.create(minute=30, hour=18)
        second = CrontabSchedule.objects.create(minute='*/50')
        result = HandleCronScheduleToTask.get_interval_to_task(first, second)
        
        self.assertEqual(result.minute, '*/50')
        
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
