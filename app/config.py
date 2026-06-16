"""Конфигурация: загрузка секретов из .env. Ключей в коде нет."""
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# понадобятся на следующих вехах
TG_API_ID = os.getenv("TG_API_ID", "")
TG_API_HASH = os.getenv("TG_API_HASH", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def require_bot_token() -> str:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN не задан. Вставь токен от @BotFather в .env "
            "(см. .env.example)."
        )
    return BOT_TOKEN
