import requests
import json
from datetime import datetime, date, time

from aiogram.utils.formatting import as_list, as_marked_section, Bold
from aiogram.enums import ParseMode

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from config.utils import find_env
from habits.models import Habit
from habits.telegram_bot.utils import construct_periodic


PATH_REMINDER_TASK = 'habits.tasks.send_habit_raminder'
TELEGRAM_SEND_MESSAGE_URL = f'https://api.telegram.org/bot{find_env("TELEGRAM_API_KEY")}/sendMessage'


def construct_time_to_task(time_interval: CrontabSchedule) -> datetime:
    """Построение актуальной даты для задач
    """
    now = date.today()
    cron_hour, cron_minute = time_interval.hour, time_interval.minute
    result = datetime(year=now.year,
                      month=now.month,
                      day=now.day,
                      hour=int(cron_hour),
                      minute=int(cron_minute),
                      tzinfo=timezone.get_current_timezone())
    return result


def create_periodic_task(user: AbstractUser, instance: Habit, validated_data: dict) -> PeriodicTask:
    """Создание рассписания задач

    Args:
        user (AbstractUser): Модель пользователя
        instance (Habit): Успешно созданая модель привычки
        validated_data (dict): Валидные данный для привычки

    Returns:
        PeriodicTask: Возвращает объект рассписания
    """    
    if not user.tg_id:
            time = construct_time_to_task(validated_data['time_to_do'])
            kwargs_to_task = json.dumps({'id_habit': instance.pk})
            task = PeriodicTask.objects.create(name=f'task_raminder_{instance.pk}/U-{user.pk}',
                                        task=PATH_REMINDER_TASK,
                                        interval=validated_data['periodic'],
                                        kwargs=kwargs_to_task,
                                        expire_seconds=settings.EXPIRE_SECONDS_TASK,
                                        start_time=time,
                                        enabled=False,
                                        )
    else:
        time = construct_time_to_task(validated_data['time_to_do'])
        kwargs_to_task = json.dumps({'id_habit': instance.pk, 'id_chat': user.tg_id})
        task = PeriodicTask.objects.create(name=f'task_raminder_{instance.pk}/U-{user.pk}',
                                    task=PATH_REMINDER_TASK,
                                    interval=validated_data['periodic'],
                                    kwargs=kwargs_to_task,
                                    expire_seconds=settings.EXPIRE_SECONDS_TASK,
                                    start_time=time,
                                    enabled=True,
                                    )
    return task


def update_periodic_task(instance: Habit, validated_data: dict) -> PeriodicTask:
    """Обновление рассписания задач

    Args:
        instance (Habit): Успешно созданая модель привычки
        validated_data (dict): Валидные данный для привычки

    Returns:
        PeriodicTask: Возвращает объект рассписания
    """
    try:
        task : PeriodicTask = PeriodicTask.objects.get(name__contains=f'_{instance.pk}')
    except:
        return
    
    time_to_do = validated_data.get('time_to_do')
    periodic = validated_data.get('periodic')
    if time_to_do:
        time = construct_time_to_task(time_to_do)
    
    match bool(time_to_do), bool(periodic):
        case True, True:
            task.interval = periodic
            task.start_time = time
            task.save(update_fields=('interval', 'start_time',))
                                               
        case False, True:
            task.interval = periodic
            task.save(update_fields=('interval',))
            
        case True, False:
            task.start_time = time
            task.save(update_fields=('start_time',))
            
        case _:
            return task
    
    return task


def construct_message(id_habit: str, id_chat: str) -> None:
    """Построение сообщения для напоминаний в Telegram
    """    
    id_chat : int = int(id_chat)
    id_habit : int = int(id_habit)
    
    params: dict = {
        'chat_id': id_chat,
        'parse_mode': ParseMode.HTML
    }
    
    try:
        habit = Habit.objects.get(pk=id_habit)
    except:
        params.update({'text': f'Привычка по ID {id_habit} не была найдена, проверьте состав привычек'})
        requests.request('POST', TELEGRAM_SEND_MESSAGE_URL, params=params)
        
    every = habit.periodic.every
    periodic = habit.periodic.period
    period = construct_periodic(every, periodic)
    
    if not habit.reward:
        related = habit.related_habit
        if related:
            related_every = habit.periodic.every
            related_periodic = habit.periodic.period
            related_period = construct_periodic(related_every, related_periodic)
            reward = as_marked_section(Bold('Награда: приятная привычка'),
                                    Bold(f'Время привычки {time(hour=int(related.time_to_do.hour), minute=int(related.time_to_do.minute)).strftime("%H:%M")}'),
                                            f'Где выполняем: {related.place}',
                                            f'Что делаем: {related.action}',
                                            f'Сколько времени нужно: {related.time_to_done}',
                                            f'С какой периодичностью: {related_period}'
                                    )
        else:
            reward = 'Наград нет'
    title = 'Приятная привычка' if habit.is_nice_habit else 'Полезная привычка'
    text = as_list(
        as_marked_section(
            Bold(title),
            Bold(f'Время привычки {time(hour=int(habit.time_to_do.hour), minute=int(habit.time_to_do.minute)).strftime("%H:%M")}'),
            marker='⏱️ ',
        ),
        as_marked_section(
            f'Где выполняем: {habit.place}',
            f'Что делаем: {habit.action}',
            f'Сколько времени нужно: {habit.time_to_done}',
            f'С какой периодичностью: {period} '
        ),
        reward,
    )
    
    params.update({'text': text.as_html()})
    requests.request('POST', TELEGRAM_SEND_MESSAGE_URL, params=params)
    