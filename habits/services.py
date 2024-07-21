import requests
import json
from datetime import datetime

from aiogram.utils.formatting import as_list, as_marked_section, Bold
from aiogram.enums import ParseMode

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from config.utils import find_env
from habits.models import Habit
from habits.telegram_bot.utils import construct_periodic
from habits.handlers import HandleCronScheduleToTask


PATH_REMINDER_TASK = 'habits.tasks.send_habit_raminder'
TELEGRAM_SEND_MESSAGE_URL = f'https://api.telegram.org/bot{find_env("TELEGRAM_API_KEY")}/sendMessage'


def construct_time_to_task(time_interval: CrontabSchedule) -> datetime:
    """Построение актуальной даты для задач
    """
    now = settings.LOCAL_TIME_NOW
    cron_hour, cron_minute = time_interval.hour, time_interval.minute
    result = datetime(year=now.year,
                      month=now.month,
                      day=now.day,
                      hour=int(cron_hour),
                      minute=int(cron_minute),
                      tzinfo=timezone.localtime(now).tzinfo)
    return result


def create_periodic_task(user: AbstractUser,
                         instance: Habit,
                         validated_data: dict,
                         ) -> PeriodicTask:
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
        crontab = HandleCronScheduleToTask.get_interval_to_task(
            validated_data['time_to_do'],
            validated_data['periodic'],
            )
        task = PeriodicTask.objects.create(
            name=f'task_raminder_{instance.pk}/U-{user.pk}',
            task=PATH_REMINDER_TASK,
            crontab=crontab,
            kwargs=kwargs_to_task,
            expire_seconds=settings.EXPIRE_SECONDS_TASK,
            start_time=time,
            enabled=False,
            )
    else:
        time = construct_time_to_task(validated_data['time_to_do'])
        kwargs_to_task = json.dumps({'id_habit': instance.pk,
                                     'id_chat': user.tg_id,
                                     })
        crontab = HandleCronScheduleToTask.get_interval_to_task(
            validated_data['time_to_do'],
            validated_data['periodic'],
            )
        task = PeriodicTask.objects.create(
            name=f'task_raminder_{instance.pk}/U-{user.pk}',
            task=PATH_REMINDER_TASK,
            crontab=crontab,
            kwargs=kwargs_to_task,
            expire_seconds=settings.EXPIRE_SECONDS_TASK,
            start_time=time,
            enabled=True,
            )
    return task


def update_periodic_task(instance: Habit,
                         validated_data: dict,
                         ) -> PeriodicTask:
    """Обновление рассписания задач

    Args:
        instance (Habit): Успешно созданая модель привычки
        validated_data (dict): Валидные данный для привычки

    Returns:
        PeriodicTask: Возвращает объект рассписания
    """
    try:
        task: PeriodicTask = PeriodicTask.objects.get(
            name__contains=f'_{instance.pk}',
            )
    except:
        return

    time_to_do = validated_data.get(
        'time_to_do',
        ) if validated_data.get(
            'time_to_do',
            ) else instance.time_to_do
    periodic = validated_data.get(
        'periodic',
        ) if validated_data.get(
            'periodic',
            ) else instance.periodic
    time = construct_time_to_task(time_to_do)

    cron = HandleCronScheduleToTask.get_interval_to_task(
        time_to_do,
        periodic,
        )
    task.crontab = cron
    task.start_time = time
    task.enabled = False
    task.save(update_fields=('crontab', 'start_time', 'enabled',))
    task.enabled = True
    task.save(update_fields=('enabled',))

    return task


def construct_message(id_habit: str, id_chat: str) -> None:
    """Построение сообщения для напоминаний в Telegram
    """
    id_chat: int = int(id_chat)
    id_habit: int = int(id_habit)

    params: dict = {
        'chat_id': id_chat,
        'parse_mode': ParseMode.HTML
    }

    try:
        habit = Habit.objects.get(pk=id_habit)
    except:
        params.update(
            {'text':
                f'Привычка по ID {id_habit} не была найдена, '
                'проверьте состав привычек'},
            )
        requests.request(
            'POST',
            TELEGRAM_SEND_MESSAGE_URL,
            params=params,
            )
        raise UnboundLocalError(
            f'{id_habit} Habit not found',
            )

    period = construct_periodic(
        habit.periodic.minute,
        habit.periodic.hour,
        habit.periodic.day_of_month,
        )
    current_time = settings.LOCAL_TIME_NOW
    if not habit.reward:
        related = habit.related_habit
        if related:
            related_period = construct_periodic(
                related.periodic.minute,
                related.periodic.hour,
                related.periodic.day_of_month,
                )
            reward = as_marked_section(
                Bold('Награда: приятная привычка'),
                Bold(
                    f'Актуальное время привычки \
                        {current_time.strftime("%H:%M")}',
                    ),
                f'Где выполняем: {related.place}',
                f'Что делаем: {related.action}',
                f'Сколько времени нужно: {related.time_to_done}',
                f'С какой периодичностью: {related_period}',
                )
        else:
            reward = 'Наград нет'
    else:
        reward = 'Наград нет'
    title = 'Приятная привычка' if habit.is_nice_habit else 'Полезная привычка'
    text = as_list(
        as_marked_section(
            Bold(title),
            Bold(f'Актуальное время привычки {current_time.strftime("%H:%M")}'),
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
