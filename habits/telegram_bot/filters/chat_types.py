from aiogram.filters import Filter
from aiogram import types


class ChatTypeFilter(Filter):

    def __init__(self, type_chat: list[str]) -> None:
        self.type_chat = type_chat

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.type_chat
