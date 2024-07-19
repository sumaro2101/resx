from datetime import timedelta
from typing import Tuple, Union

from rest_framework.validators import ValidationError

from django_celery_beat.models import IntervalSchedule, CrontabSchedule


class HandleInterval:
    """Обработчик интервала
    """
    
    @classmethod
    def _get_parse_interval(cls, value: Union[str, None]) -> Tuple[int, str]:
        """Парсинг интервала
        """
        if not isinstance(value, Union[str, None]):
            raise TypeError(f'Значение {value} не является интервалом времени')
        if value:
            try:        
                days, hours, minute = value.split('/')
            except:
                raise ValueError(f'{value}, не соответствует стандарту по типу: "30/0/0"')
            
        if not value:
            return 1, IntervalSchedule.DAYS
        elif int(days):
            return int(days), IntervalSchedule.DAYS
        elif int(hours):
            return int(hours), IntervalSchedule.HOURS
        elif int(minute):
            return int(minute), IntervalSchedule.MINUTES
    
    @classmethod
    def _get_or_set_interval(cls, value: int, type_of_time: str) -> IntervalSchedule:
        """Получение или создание интервала
        """
        interval = IntervalSchedule.objects.filter(every=value, period=type_of_time)
        if not interval.exists():
            interval = IntervalSchedule.objects.create(every=value, period=type_of_time)
            return interval            
        return interval.get()
            
    @classmethod
    def get_interval(cls, value: Union[str, None]) -> IntervalSchedule:
        """Получение интервала времени

        Args:
            value (str): Значение интервала строковый тип
        """        
        value, type_of_time = cls._get_parse_interval(value)
        
        return cls._get_or_set_interval(value=value, type_of_time=type_of_time)


class HandleTimeToDo:
    """Обработчик времени тип Час : Минута
    """
    
    @classmethod
    def _parse_time(cls, value: str) -> Tuple[int]:
        """Парсинг времени
        """
        if not isinstance(value, str):
            raise TypeError(f'{value}, должен быть строкой')
        try:
            hour, minute = [int(value) for value in value.split(':')]
        except:
            ValueError('Время должно быть конструкцией тип: "23:30"')
        
        return hour, minute
    
    @classmethod
    def _get_or_set_crontab_time(cls, hour: int, minute: int) -> CrontabSchedule:
        """Получение или создание Crontab времени
        """
        crontab_time = CrontabSchedule.objects.filter(hour=hour, minute=minute)
        if not crontab_time.exists():
            crontab_time = CrontabSchedule.objects.create(hour=hour, minute=minute)
            return crontab_time
        return crontab_time.get()
    
    @classmethod
    def get_crontab_time(cls, value: str) -> CrontabSchedule:
        """Вывод Crontab времени из полученной строки

        Args:
            value (str): Строка с временем

        Returns:
            CrontabSchedule: CrontabSchedule
        """        
        hour, minute = cls._parse_time(value)
        crontab_time = cls._get_or_set_crontab_time(hour=hour, minute=minute)
        return crontab_time


class HandleTimeToDone:
    """Обработчик времени тип Минута : Секунда
    """
    
    @classmethod
    def _parse_time(cls, value: str) -> Tuple[int]:
        """Парсинг времени
        """
        if not isinstance(value, str):
            raise TypeError(f'{value}, должен быть строкой')
        try:
            minutes, seconds = [int(value) for value in value.split(':')]
        except:
            raise ValueError('Время должно быть конструкцией тип: "01:30"')
        
        return minutes, seconds
    
    @classmethod
    def get_time(cls, value: str) -> timedelta:
        """Вывод timedelta времени
        """
        minutes, seconds = cls._parse_time(value)
        time = timedelta(minutes=minutes, seconds=seconds)
        return time
    