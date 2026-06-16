"""Коннектор к Telegram-каналам через Telethon (user-сессия). Веха 1.

Читаем публичные каналы как обычный пользователь. Сессия хранится в
файле krasnodar_events.session (gitignored). Первый вход — интерактивный
(scripts/tg_login.py), дальше сессия переиспользуется.
"""
from telethon import TelegramClient

from app.config import TG_API_ID, TG_API_HASH
from app.connectors import CHANNELS  # noqa: F401 (общий список каналов)

SESSION_NAME = "krasnodar_events"


def get_client() -> TelegramClient:
    if not TG_API_ID or not TG_API_HASH:
        raise RuntimeError(
            "TG_API_ID / TG_API_HASH не заданы. Заполни .env (см. .env.example)."
        )
    return TelegramClient(SESSION_NAME, int(TG_API_ID), TG_API_HASH)


async def fetch_channel(client: TelegramClient, channel: str, limit: int = 30) -> list[dict]:
    """Вернуть последние посты канала как список сырых записей."""
    posts: list[dict] = []
    async for msg in client.iter_messages(channel, limit=limit):
        if not msg.message:  # пропускаем медиа без текста
            continue
        posts.append(
            {
                "source": channel,
                "msg_id": msg.id,
                "posted_at": msg.date.isoformat() if msg.date else None,
                "text": msg.message,
            }
        )
    return posts
