import asyncio
import django
import os

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
if not settings.configured:
    django.setup()
    
from aiogram import Bot, Dispatcher, types

from handlers.user_private import user_private_router
from common_commands.bot_common_cmd import private

from config.utils import find_env

ALLOWED_UPDATES = ['message', 'edited_message']

bot = Bot(token=find_env('TELEGRAM_API_KEY'))

dispatcher = Dispatcher()

dispatcher.include_router(user_private_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dispatcher.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

asyncio.run(main())
