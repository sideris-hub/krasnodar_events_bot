"""Точка входа. Веха 0: поднимаем бота на long-polling, хендлер /start.

Дальше сюда подключатся scheduler (парсинг + пятничный дайджест) и
остальные модули пайплайна.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import require_bot_token
from app.bot.handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(token=require_bot_token())
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Бот запущен, начинаю polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
