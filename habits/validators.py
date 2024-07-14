from rest_framework.validators import ValidationError
from typing import Any, Tuple


class ValidateInterval:
    """Валидатор который проверяет корректность временного интервала
    """
    def __init__(self, field: str) -> None:
        if not isinstance(field, str):
            raise TypeError(f'{field} должен быть строкой')
        self.field = field
        
    def _check_interval_values(self, day: int, hour: int, minute: int) -> None:
        """Проверка интервала на нахождение значений
        """
        # Проверка пустых значений в интервале
        if not any((day, hour, minute)):
                raise ValidationError('Указанный интервал не может быть пустым, нужно указать одно из значений')
        
        # Проверка на множественное указание значений в интервале
        have_value = False
        for value in (day, hour, minute):
            if value and have_value:
                raise ValidationError('В интервале нельзя указывать одновременно день или час или минуты')
            elif value and not have_value:
                have_value = True
                
    def _check_is_interval_type(self, value: str) -> Tuple[int]:
        """
        Проверка на интервал тип
        Args:
            value (str): Строка с предпологаемым интервалом

        Returns:
            Tuple[int]: Возращает кортеж из интервала
        """
        if not isinstance(value, str):
            raise ValidationError(f'{value} должен быть строкой')
        if value.find(' ') >= 0:
            raise ValidationError(f'{value} имеет пробелы, это не допустимо')
        try:
            day, hour, minute = [int(value) for value in value.split('/')]
        except:
            raise ValidationError(f'{value} должен быть интервалом по типу "7/0/0" что значит интервал из 7 дней')
        self._check_interval_values(day, hour, minute)
        
        return day, hour, minute
    
    def __day(self, day: int) -> bool:
        """Проверка значение дня
        """
        return 0 <= day < 8
    
    def __hour(self, hour: int) -> bool:
        """Проверка значения часа
        """
        return 0 <= hour < 23
    
    def __minute(self, minute: int) -> bool:
        """Проверка значения минуты
        """        
        return 0 <= minute < 59
    
    def _check_interval(self, value: str) -> None:
        """Точка входа для проверки интервала
        """        
        day, hour, minute = self._check_is_interval_type(value)
        day = self.__day(day)
        hour = self.__hour(hour)
        minute = self.__minute(minute)
        
        if not day:
            raise ValidationError(f'Значение day может быть больше или равно нулю, либо не более чем 7')
        if not hour:
            raise ValidationError(f'Значение hour не корректное')
        if not minute:
            raise ValidationError(f'Значение minute не корректное')
        
    def __call__(self, attrs) -> Any:
        checked_values = [
                value for field, value in attrs.items() if field in self.field
                and not None
            ]
        if checked_values:
            self._check_interval(checked_values[0])


class ValidateDateTwoPart:
    """Валидация времени состоящее из двух частей
    """
    
    def __init__(self, date: str) -> None:
        if not isinstance(date, str):
            raise TypeError(f'{date} должен быть строкой')
        self.checked_values = self._check_two_part(date)
        
    def _check_two_part(self, date: str) -> Tuple[int]:
        """Проверка времени состоящих из двух частей

        Args:
            date (str): Время

        Returns:
            Tuple[int]: В случае успеха возращает кортеж из чисел
        """        
        if date.find(' ') >= 0:
            raise ValidationError(f'{date} имеет пробелы, это не допустимо')
        try:
            first, second = date.split(':')
        except:
            raise ValidationError(f'{date} не является корректным для данного поля, необходимо использовать разделитель ":" и стандартный вид должен быть: "18:30"')
        
        try:
            first, second = [int(value) for value in [first, second]]
        except:
            raise ValidationError('Значения в времени могут быть только циферными')
        
        return first, second
    

class ValidateDateDay:
    """Валидация времени тип День
    """    
    def __init__(self, field: str) -> None:
        if not isinstance(field, str):
            raise TypeError(f'{field} должен быть строкой')
        self.field = field
    
    def __hour(self, hour: int) -> bool:
        """Проверка значения часа
        """
        return 0 <= hour < 24
    
    def __minute(self, minute: int) -> bool:
        """Проверка значения минуты
        """        
        return 0 <= minute < 60
    
    def _check_hour_minute_values(self, hour: int, minute: int) -> None:
        """Проверка часа и минуты
        """        
        hour = self.__hour(hour)
        minute = self.__minute(minute)
        
        if not hour:
            raise ValidationError(f'Значение hour не корректное')
        if not minute:
            raise ValidationError(f'Значение minute не корректное')
        
    def __call__(self, attrs) -> Any:
        checked_values = [
                value for field, value in attrs.items() if field in self.field
                and not None
            ]
        if checked_values:
            hour, minute = ValidateDateTwoPart(checked_values[0]).checked_values
            self._check_hour_minute_values(int(hour), int(minute))
            
            
class ValidateDateMinute:
    """Валидация времени тип Минуты
    """    
    def __init__(self, field: str) -> None:
        if not isinstance(field, str):
            raise TypeError(f'{field} должен быть строкой')
        self.field = field
        
    def __minute(self, minute: int) -> bool:
        """Проверка значения минуты
        """        
        return 0 <= minute < 60
    
    def __second(self, second: int) -> bool:
        """Проверка значения минуты
        """        
        return 0 <= second < 60
    
    def _is_less_two_minutes(self, minute: int, second: int) -> None:
        if minute >= 2 and second:
            raise ValidationError('Было полученно более двух минут!')
        
    def _check_minute_second_values(self, minute: int, second: int) -> None:
        valide_minute = self.__minute(minute)
        valide_second = self.__second(second)
        
        if not valide_minute:
            raise ValidationError(f'Значение minute не корректное')
        if not valide_second:
            raise ValidationError(f'Значение second не корректное')
        self._is_less_two_minutes(minute, second)
        
    def __call__(self, attrs) -> Any:
        checked_values = [
                value for field, value in attrs.items() if field in self.field
                and not None
            ]
        if checked_values:
            minute, second = ValidateDateTwoPart(checked_values[0]).checked_values
            self._check_minute_second_values(int(minute), int(second))
            