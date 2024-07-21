from rest_framework.validators import ValidationError

from django.test import TestCase
from django.contrib.auth import get_user_model

from django_celery_beat.models import CrontabSchedule

from datetime import timedelta

from habits.validators import (ValidateInterval,
                               ValidateDateTwoPart,
                               ValidateDateDay,
                               ValidateDateMinute,
                               ValidatorOneValueInput,
                               ValidatorNiceHabit,
                               ValidatorRalatedHabit,
                               )
from habits.models import Habit


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
        interval = CrontabSchedule.objects.create(minute=0, hour=0, day_of_month='*/1')
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
        interval = CrontabSchedule.objects.create(minute=0, hour=0, day_of_month='*/1')
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
