from datetime import timedelta
from typing import Tuple, Union

from django_celery_beat.models import CrontabSchedule


class HandleInterval:
    """Обработчик интервала
    """

    @classmethod
    def _get_parse_interval(cls,
                            value: Union[str, None],
                            ) -> Tuple[int, str]:
        """Парсинг интервала
        """
        if not isinstance(value, Union[str, None]):
            raise TypeError(
                f'Значение {value} не является интервалом времени',
                )
        if value:
            try:
                days, hours, minute = value.split('/')
            except:
                raise ValueError(
                    f'{value}, не соответствует стандарту по типу: "30/0/0"',
                    )

        if not value:
            return '*/1', 'days'
        elif int(days):
            return f'*/{int(days)}', 'days'
        elif int(hours):
            return f'*/{int(hours)}', 'hours'
        elif int(minute):
            return f'*/{int(minute)}', 'minutes'

    @classmethod
    def _get_or_set_interval(cls,
                             value: int,
                             type_of_time: str) -> CrontabSchedule:
        """Получение или создание интервала
        """
        match value, type_of_time:
            case _, 'days':
                interval = CrontabSchedule.objects.filter(
                    minute='*',
                    hour='*',
                    day_of_month=value,
                    )
                if not interval.exists():
                    interval = CrontabSchedule.objects.create(
                        minute='*',
                        hour='*',
                        day_of_month=value,
                        )
                    return interval
                return interval.get()

            case _, 'hours':
                interval = CrontabSchedule.objects.filter(
                    minute='*',
                    hour=value,
                    day_of_month='*',
                    )
                if not interval.exists():
                    interval = CrontabSchedule.objects.create(
                        minute='*',
                        hour=value,
                        day_of_month='*',
                        )
                    return interval
                return interval.get()

            case _, 'minutes':
                interval = CrontabSchedule.objects.filter(
                    minute=value,
                    hour='*',
                    day_of_month='*',
                    )
                if not interval.exists():
                    interval = CrontabSchedule.objects.create(
                        minute=value,
                        hour='*',
                        day_of_month='*',
                        )
                    return interval
                return interval.get()

    @classmethod
    def get_interval(cls,
                     value: Union[str, None],
                     ) -> CrontabSchedule:
        """Получение интервала времени

        Args:
            value (str): Значение интервала строковый тип
        """
        value, type_of_time = cls._get_parse_interval(value)

        return cls._get_or_set_interval(
            value=value,
            type_of_time=type_of_time,
            )


class HandleTimeToDo:
    """Обработчик времени тип Час : Минута
    """

    @classmethod
    def _parse_time(cls, value: str) -> Tuple[int]:
        """Парсинг времени
        """
        if not isinstance(value, str):
            raise TypeError(
                f'{value}, должен быть строкой'
                )
        try:
            hour, minute = [int(value)
                            for value
                            in value.split(':')]
        except:
            ValueError(
                'Время должно быть конструкцией тип: "23:30"',
                )

        return hour, minute

    @classmethod
    def _get_or_set_crontab_time(cls,
                                 hour: int,
                                 minute: int,
                                 ) -> CrontabSchedule:
        """Получение или создание Crontab времени
        """
        crontab_time = CrontabSchedule.objects.filter(
            hour=hour,
            minute=minute,
            day_of_month='*',
            )
        if not crontab_time.exists():
            crontab_time = CrontabSchedule.objects.create(
                hour=hour,
                minute=minute,
                day_of_month='*',
                )
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
        crontab_time = cls._get_or_set_crontab_time(
            hour=hour,
            minute=minute,
            )
        return crontab_time


class HandleTimeToDone:
    """Обработчик времени тип Минута : Секунда
    """

    @classmethod
    def _parse_time(cls, value: str) -> Tuple[int]:
        """Парсинг времени
        """
        if not isinstance(value, str):
            raise TypeError(
                f'{value}, должен быть строкой',
                )
        try:
            minutes, seconds = [int(value)
                                for value
                                in value.split(':')]
        except:
            raise ValueError(
                'Время должно быть конструкцией тип: "01:30"',
                )

        return minutes, seconds

    @classmethod
    def get_time(cls, value: str) -> timedelta:
        """Вывод timedelta времени
        """
        minutes, seconds = cls._parse_time(value)
        time = timedelta(minutes=minutes, seconds=seconds)
        return time


class HandleCronScheduleToTask:
    """Обработка кронтабов для задачи
    """

    @classmethod
    def _check_cron_instance(cls,
                             cron_to_do: CrontabSchedule,
                             cron_interval: CrontabSchedule,
                             ) -> None:
        """Проверка кронтабов
        """
        if not isinstance(cron_to_do, CrontabSchedule):
            raise TypeError(
                f'{cron_to_do}, должен быть CrontabSchedule',
                )
        if not isinstance(cron_interval, CrontabSchedule):
            raise TypeError(
                f'{cron_interval}, должен быть CrontabSchedule',
                )

    @classmethod
    def _parse_cron_intervals(cls,
                              cron_to_do: CrontabSchedule,
                              cron_interval: CrontabSchedule,
                              ) -> tuple:
        """Парсит время для одной задачи
        """
        minute = '*'
        hour = '*'
        day_of_month = '*'

        if cron_interval.minute != '*':
            minute = cron_interval.minute
            return minute, hour, day_of_month

        elif cron_interval.hour != '*':
            minute = 0
            hour = cron_interval.hour
            return minute, hour, day_of_month

        else:
            minute = cron_to_do.minute
            hour = cron_to_do.hour
            day_of_month = cron_interval.day_of_month
            return minute, hour, day_of_month

    @classmethod
    def _get_or_set_crontab_time(cls,
                                 minute: int,
                                 hour: int,
                                 day_of_month: str,
                                 ) -> CrontabSchedule:
        """Получение или создание Crontab времени
        """
        crontab_time = CrontabSchedule.objects.filter(
            hour=hour,
            minute=minute,
            day_of_month=day_of_month,
            )
        if not crontab_time.exists():
            crontab_time = CrontabSchedule.objects.create(
                hour=hour,
                minute=minute,
                day_of_month=day_of_month,
                )
            return crontab_time
        return crontab_time.get()

    @classmethod
    def get_interval_to_task(cls,
                             cron_to_do: CrontabSchedule,
                             cron_interval: CrontabSchedule,
                             ) -> CrontabSchedule:
        """Перерабатывает два кронтаб объекта в один для задач
        """
        cls._check_cron_instance(cron_to_do,
                                 cron_interval,
                                 )
        minute, hour, day_of_month = cls._parse_cron_intervals(
            cron_to_do,
            cron_interval,
            )
        return cls._get_or_set_crontab_time(
            minute,
            hour,
            day_of_month,
            )
