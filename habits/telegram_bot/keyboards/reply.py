from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Список'),
            KeyboardButton(text='Следующая'),
            KeyboardButton(text='Инфо'),
            KeyboardButton(text='Авторизация', request_contact=True),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?',
)
