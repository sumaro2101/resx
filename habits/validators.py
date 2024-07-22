from rest_framework.validators import ValidationError

from typing import Any, Callable, List, Tuple


class ValidateInterval:
    """Валидатор который проверяет корректность временного интервала
    """
    def __init__(self, field: str) -> None:
        if not isinstance(field, str):
            raise TypeError(
                f'{field} должен быть строкой',
                )
        self.field = field

    def _check_interval_values(self, day: int, hour: int, minute: int) -> None:
        """Проверка интервала на нахождение значений
        """
        # Проверка пустых значений в интервале
        if not any((day, hour, minute)):
            raise ValidationError(
                {self.field: 'Указанный интервал не может быть пустым, '
                 'нужно указать одно из значений'},
                )

        # Проверка на множественное указание значений в интервале
        have_value = False
        for value in (day, hour, minute):
            if value and have_value:
                raise ValidationError(
                    {self.field: 'В интервале нельзя указывать '
                     'одновременно день или час или минуты'},
                    )
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
            raise ValidationError(
                {self.field: f'{value} должен быть строкой'},
                )
        if value.find(' ') >= 0:
            raise ValidationError(
                {self.field: f'{value} имеет пробелы, это не допустимо'},
                )
        try:
            day, hour, minute = [int(value)
                                 for value
                                 in value.split('/')
                                 ]
        except ValueError:
            raise ValidationError(
                {self.field:
                    f'{value} должен быть интервалом '
                    'по типу "7/0/0" что значит интервал из 7 дней',
                 },
                )
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
            raise ValidationError(
                {self.field:
                    'Значение day '
                    'может быть больше или равно нулю, либо не более чем 7',
                 },
                )
        if not hour:
            raise ValidationError(
                {self.field:
                    'Значение hour '
                    'не может быть меньше 0 или больше чем 59',
                 },
                )
        if not minute:
            raise ValidationError(
                {self.field:
                    'Значение minute '
                    'не может быть меньше 0 или больше чем 59',
                 },
                )

    def __call__(self, attrs) -> Any:
        checked_values = [
                value
                for field, value
                in attrs.items()
                if field == self.field
                and not None
            ]
        if checked_values:
            self._check_interval(checked_values[0])


class ValidateDateTwoPart:
    """Валидация времени состоящее из двух частей
    """

    def __init__(self, date: str) -> None:
        if not isinstance(date, str):
            raise TypeError(
                f'{date} должен быть строкой',
                )
        self.date = date
        self.checked_values = self._check_two_part(self.date)

    def _check_two_part(self, date: str) -> Tuple[int]:
        """Проверка времени состоящих из двух частей

        Args:
            date (str): Время

        Returns:
            Tuple[int]: В случае успеха возращает кортеж из чисел
        """
        if date.find(' ') >= 0:
            raise ValidationError(
                {self.date: f'{date} имеет пробелы, это не допустимо'},
                )
        try:
            minute, seconds = date.split(':')
        except ValueError:
            raise ValidationError(
                {
                    self.date:
                        f'{date} не является корректным для данного поля, '
                        'необходимо использовать разделитель ":" '
                        'и стандартный вид должен быть: "18:30"',
                        },
                )

        try:
            minute, seconds = [
                int(value)
                for value
                in [minute, seconds]
                ]
        except ValueError:
            raise ValidationError(
                {self.date: 'Значения в времени могут быть только циферными'},
                )

        return minute, seconds


class ValidateDateDay:
    """Валидация времени тип День
    """
    def __init__(self, field: str) -> None:
        if not isinstance(field, str):
            raise TypeError(
                f'{field} должен быть строкой',
                )
        self.field = field

    def __hour(self, hour: int) -> bool:
        """Проверка значения часа
        """
        return 0 <= hour < 24

    def __minute(self, minute: int) -> bool:
        """Проверка значения минуты
        """
        return 0 <= minute < 60

    def _check_hour_minute_values(self,
                                  hour: int,
                                  minute: int,
                                  ) -> None:
        """Проверка часа и минуты
        """
        hour = self.__hour(hour)
        minute = self.__minute(minute)

        if not hour:
            raise ValidationError(
                {self.field: 'Значение hour '
                 'не может быть меньше 0 или больше 23'},
                )
        if not minute:
            raise ValidationError(
                {self.field: 'Значение minute '
                 'не может быть меньше 0 или больше 59'},
                )

    def __call__(self, attrs) -> Any:
        checked_values = [
                value
                for field, value
                in attrs.items()
                if field == self.field
                and not None
            ]
        if checked_values:
            hour, minute = ValidateDateTwoPart(
                checked_values[0],
                ).checked_values
            self._check_hour_minute_values(int(hour),
                                           int(minute),
                                           )


class ValidateDateMinute:
    """Валидация времени тип Минуты
    """
    def __init__(self, field: str) -> None:
        if not isinstance(field, str):
            raise TypeError(
                f'{field} должен быть строкой',
                )
        self.field = field

    def __minute(self, minute: int) -> bool:
        """Проверка значения минуты
        """
        return 0 <= minute < 60

    def __second(self, second: int) -> bool:
        """Проверка значения минуты
        """
        return 0 <= second < 60

    def _is_less_two_minutes(self,
                             minute: int,
                             second: int,
                             ) -> None:
        if minute >= 2 and second:
            raise ValidationError(
                {self.field: 'Было полученно более двух минут!'},
                )

    def _check_minute_second_values(self,
                                    minute: int,
                                    second: int,
                                    ) -> None:
        valide_minute = self.__minute(minute)
        valide_second = self.__second(second)

        if not valide_minute:
            raise ValidationError(
                {self.field: 'Значение minute не корректное'},
                )
        if not valide_second:
            raise ValidationError(
                {self.field: 'Значение second не корректное'},
                )
        self._is_less_two_minutes(minute, second)

    def __call__(self, attrs) -> Any:
        checked_values = [
                value
                for field, value
                in attrs.items()
                if field == self.field
                and not None
            ]
        if checked_values:
            minute, second = ValidateDateTwoPart(
                checked_values[0],
                ).checked_values
            self._check_minute_second_values(int(minute), int(second))


class ValidatorOneValueInput:
    """Валидатор который проверяет
    что из двух полей только одно из них выбрано
    """
    def __init__(self,
                 fields: List[str],
                 ) -> None:
        if not isinstance(fields, list):
            raise TypeError(
                'Поле "fields" должно было List',
                )
        if len(fields) != 2:
            raise KeyError(
                'Неоходимо указать два значения для проверки',
                )
        for field in fields:
            if not isinstance(field, str):
                raise TypeError(
                    'Аргумент "field" может быть только строкой',
                    )
        self.fields = fields

    def __call__(self, attrs: Any) -> Callable:
        checked_values = [
                value
                for field, value
                in attrs.items()
                if field in self.fields
                and value is not None
            ]
        if len(checked_values) > 1:
            raise ValidationError(
                {'error':
                    f'{self.fields[0]} и {self.fields[-1]} '
                    'не могут быть определенны вместе',
                 },
                )


class ValidatorNiceHabit:
    """Валидация приятной привычки
    Первым аргументом нужно указать поле
    по которому будет определяться является ли объект приятной привычкой
    Второй это список из двух полей которые должны контроллироваться
    """
    def __init__(self,
                 nice_habbit: str,
                 fields: List[str],
                 ) -> None:
        if not isinstance(fields, List):
            raise TypeError(
                'Поле "fields" должно было List',
                )
        if len(fields) != 3:
            raise ValueError(
                'Неоходимо указать три значения для проверки',
                )
        if not isinstance(nice_habbit, str):
            raise TypeError(
                'Поле related_field должен быть str',
                )
        if nice_habbit not in fields:
            raise ValueError(
                f'Значение {nice_habbit}, должен быть в составе {fields}',
                )
        for field in fields:
            if not isinstance(field, str):
                raise TypeError(
                    f'Аргумент {field} может быть только строкой',
                    )
        self.nice_habbit = nice_habbit
        self.fields = fields

    def __call__(self, attrs) -> Any:
        checked_values = {
                field: bool(value)
                for field, value
                in attrs.items()
                if field in self.fields
        }
        if checked_values and checked_values.get(self.nice_habbit):
            if any(
                (value
                 for field, value
                 in checked_values.items()
                 if field not in self.nice_habbit),
            ):
                raise ValidationError(
                    {self.nice_habbit:
                        'При указании приятной привычки '
                        'награду и связаную привычку указывать нельзя',
                     },
                    )


class ValidatorRalatedHabit:
    """Валидатор связаной привычки
    """
    def __init__(self, field: str) -> None:
        if not isinstance(field, str):
            raise TypeError(f'{field} должен быть строкой')
        self.field = field

    def __call__(self, attrs) -> Any:
        checked_values = [
                value
                for field, value
                in attrs.items()
                if field == self.field
                and value is not None
            ]

        if checked_values:
            if not checked_values[0].is_nice_habit:
                raise ValidationError(
                    {self.field:
                        'Связаная привычка может быть только приятной',
                     },
                    )


class ValidatorRelatedHabitSomePublished:
    """Валидатор одинаковых статусов публичности
    """
    def __init__(self, related_habbit: str, fields: List[str]) -> None:
        if not isinstance(fields, List):
            raise TypeError(
                'Поле "fields" должно было List',
                )
        if len(fields) != 2:
            raise ValueError(
                 'Неоходимо указать три значения для проверки',
                )
        if not isinstance(related_habbit, str):
            raise TypeError(
                'Поле related_field должен быть str',
                )
        if related_habbit not in fields:
            raise ValueError(
                f'Значение {related_habbit}, должен быть в составе {fields}',
                )
        for field in fields:
            if not isinstance(field, str):
                raise TypeError(
                    f'Аргумент {field} может быть только строкой',
                    )
        self.related_habbit = related_habbit
        self.fields = fields

    def __call__(self, attrs) -> Any:
        checked_values = {
                field: value
                for field, value
                in attrs.items()
                if field in self.fields
        }
        related_habbit = checked_values.get(self.related_habbit)
        if checked_values and related_habbit:
            if checked_values.get(
                self.fields[-1]
                if self.fields[-1] != self.related_habbit
                else self.fields[0]
            ) != related_habbit.is_published:
                raise ValidationError(
                    {self.related_habbit:
                        'Связанная привычка и текущая '
                        'не могут иметь разные статусы публичности'
                     },
                    )
