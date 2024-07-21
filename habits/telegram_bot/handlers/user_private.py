import json

from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.enums import ParseMode

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse

from django_celery_beat.models import PeriodicTask

from filters.chat_types import ChatTypeFilter
from habits.models import Habit
from keyboards.reply import start_kb
from utils import get_list_habits, get_next_habit, get_info


REGISTER_USER_URL = f'http://127.0.0.1:8000{reverse("users:user_create")}'


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(('private',)))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        'Привет я помогу вам если вам нужно будет напомнить о вашей привычки',
        reply_markup=start_kb,
        )


@user_private_router.message(
    or_f(Command('list'), F.text.lower().contains('список')),
    )
async def list_habits(message: types.Message):
    """Вывод списка привычек
    """
    try:
        user = await get_user_model().objects.aget(tg_id=message.chat.id)
    except:
        await message.answer(
            f'{message.from_user.first_name}, вы не авторизованы',
            )
        return

    list_of_habits = Habit.objects.filter(
        owner=user,
        ).select_related(
            'time_to_do',
            'periodic',
            )
    if await list_of_habits.aexists():
        text = await get_list_habits(list_of_habits)
    else:
        text = 'Привычек пока что нет'
    await message.answer(text, parse_mode=ParseMode.HTML)


@user_private_router.message(
    or_f(Command('next'), F.text.lower().contains('следующая')),
    )
async def next(message: types.Message):
    """Вывод следующей привычки
    """
    try:
        user = await get_user_model().objects.aget(tg_id=message.chat.id)
    except:
        await message.answer(
            f'{message.from_user.first_name}, вы не авторизованы',
            )
        return

    list_of_habits = Habit.objects.filter(
        owner=user,
        ).select_related(
            'time_to_do',
            'periodic',
            )
    if await list_of_habits.aexists():
        text = await get_next_habit(list_of_habits)
    else:
        text = 'Привычек пока что нет'
    await message.answer(text, parse_mode=ParseMode.HTML)


@user_private_router.message(
    or_f(Command('info'), F.text.lower().contains('инфо')),
    )
async def info(message: types.Message):
    """Вывод следующей привычки
    """
    try:
        user = await get_user_model().objects.aget(
            tg_id=message.chat.id,
            )
    except:
        await message.answer(
            f'{message.from_user.first_name}, вы не авторизованы',
            )
        return
    text = await get_info(user)
    await message.answer(text, parse_mode=ParseMode.HTML)


@user_private_router.message(F.contact)
async def phone(message: types.Message):
    phone = f'+{message.contact.phone_number}'

    try:
        user = await get_user_model().objects.aget(phone=phone)
    except:
        await message.answer(
            f'{message.from_user.first_name}, '
            'мы не смогли найти вашу учетную запись, '
            'возможно вы до сих по не зарегистрированы, '
            f'если это так перейдите по ссылке: {REGISTER_USER_URL}',
            )
        return

    if not user.tg_id:
        user.tg_id = message.chat.id
        await user.asave(update_fields=('tg_id',))
        await message.answer(
            f'{message.from_user.first_name}, '
            'вы были успешно авторизованы',
            )
    else:
        await message.answer(
            f'{message.from_user.first_name}, '
            'вы уже авторизованы',
            )
        return

    tasks = PeriodicTask.objects.filter(
        Q(name__contains=f'U-{user.pk}'),
        )

    if not await tasks.aexists():
        await message.answer('В данный момент у вас не единной привычки')
    else:
        async for task in tasks.filter(~Q(enabled=True)):
            task.enabled = True
            kwargs = json.loads(task.kwargs)
            kwargs.update({'id_chat': message.chat.id})
            task.kwargs = json.dumps(kwargs)
            await task.asave(
                update_fields=('enabled', 'kwargs',),
                )

        await message.answer(
            f'У вас есть {await user.habit_set.acount()} привычки',
            )
