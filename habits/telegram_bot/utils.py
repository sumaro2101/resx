from typing import Union

from django.db.models import QuerySet, Q
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from habits.models import Habit

def construct_periodic(minute: str, hour: str, day_of_month: str) -> str:
    """Создает текстовое представление из интервала
    """
    
    match minute, hour, day_of_month:
        case '*', '*', day_of_month:
            match day_of_month := int(day_of_month.split('/')[-1]):
                case 1:
                    return 'Каждый день'
                case 2 | 3 | 4:
                    return f'Каждые {day_of_month} дня'
                case _:
                    return f'Каждые {day_of_month} дней'
        case '*', hour, '*':
            match hour := int(hour.split('/')[-1]):
                case 1:
                    return 'Каждый час'
                case 2 | 3 | 4 | 22 | 23:
                    return f'Каждые {hour} часа'
                case 21:
                    return f'Каждый {hour} час'
                case _:
                    return f'Каждые {hour} часов'
        case minute, '*', '*':
            match minute := int(minute.split('/')[-1]):
                case 1:
                    return 'Каждую минуту'
                case 2 | 3 | 4 | 22 | 23 | 24 | 32 | 33 | 34 | 42 | 43 | 44 | 52 | 53 | 54:
                    return f'Каждые {minute} минуты'
                case 21 | 31 | 41 | 51:
                    return f'Каждую {minute} минуту'
                case _:
                    return f'Каждые {minute} минут'
 
               
async def get_list_habits(list_of_habits: QuerySet[Habit]) -> str:
    """Конвертация списка привычек в текст
    """    
    text = ''
    
    async for habit in list_of_habits:
        time = f"{habit.time_to_do.hour}" + ":" + (f"0{habit.time_to_do.minute}" if int(habit.time_to_do.minute) < 10 else habit.time_to_do.minute)
        title = f"😌 <b>Приятная привычка</b>" if habit.is_nice_habit else "🧐 <b>Полезная привычка</b>"
        text += f'{title}\n👉 Что делаем: {habit.action}\n⏱️ В какое время: {time}\n⏲️ Периодичность: {construct_periodic(habit.periodic.minute, habit.periodic.hour, habit.periodic.day_of_month)}\n\n'
    return text


async def get_next_habit(list_of_habits: QuerySet[Habit]) -> str:
    """Вывод следующей привычки
    """    
    local_time = settings.LOCAL_TIME_NOW
    
    next_habit : Habit = await list_of_habits.filter(Q(time_to_do__hour__gte=local_time.hour)).afirst()
    if next_habit:
        time = f"{next_habit.time_to_do.hour}" + ":" + (f"0{next_habit.time_to_do.minute}" if int(next_habit.time_to_do.minute) < 10 else next_habit.time_to_do.minute)
        title = f"😌 <b>Приятная привычка</b>" if next_habit.is_nice_habit else "🧐 <b>Полезная привычка</b>"
        text = f'<b>Следующая привычка</b>\n{title}\n👉 Что делаем: {next_habit.action}\n⏱️ В какое время: {time}\n⏲️ Периодичность: {construct_periodic(next_habit.periodic.minute, next_habit.periodic.hour, next_habit.periodic.day_of_month)}\n\n'
    else:
        text = 'На сегодня привычек больше нет'

    return text


async def get_info(user: AbstractUser) -> str:
    """Создание информации о пользователе
    """    
    text = f'Вы зарегистрированы на сайте под именем <b>{user.get_username()}</b>\n\
📧 Ваш эмеил: {user.email}\n\
📱 Ваш телефон: {user.phone}\n\
- Количество полезных привычек: {await user.habit_set.filter(is_nice_habit=False).acount()}\n\
- Количество приятных привычек: {await user.habit_set.filter(is_nice_habit=True).acount()}'
    return text
