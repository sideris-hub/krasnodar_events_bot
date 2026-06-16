"""Хендлеры Telegram-бота. Веха 0: только /start."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я собираю интересные события Краснодара под твои темы "
        "(IT/AI, спорт-актив, музыка) и присылаю подборками.\n\n"
        "Пока я на этапе сборки — кнопки и афиша появятся на следующих вехах. "
        "Скелет жив и на связи 🛠"
    )
