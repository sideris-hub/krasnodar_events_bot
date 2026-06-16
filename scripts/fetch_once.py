"""Разовый парсинг всех каналов -> нормализация -> сохранение в БД. Веха 1.

Использует Telethon-сессию (сначала пройди вход: scripts/tg_login_qr.py).
Запуск из корня проекта:  python -m scripts.fetch_once
"""
import asyncio

from app.connectors import CHANNELS
from app.connectors.telegram import fetch_channel, get_client
from app.parser.extract import extract_hints
from app.storage.db import count_events, init_db, save_event


async def main() -> None:
    init_db()
    client = get_client()
    await client.connect()
    if not await client.is_user_authorized():
        print("Нет сессии. Сначала пройди вход: python -m scripts.tg_login_qr")
        await client.disconnect()
        return

    total_new = 0
    for channel in CHANNELS:
        try:
            posts = await fetch_channel(client, channel, limit=30)
        except Exception as exc:  # канал недоступен / закрыт / опечатка
            print(f"{channel}: ошибка — {exc}")
            continue

        new = 0
        for post in posts:
            post.update(extract_hints(post["text"]))
            if save_event(post):
                new += 1
        print(f"{channel}: получено {len(posts)}, новых {new}")
        total_new += new

    await client.disconnect()
    print(f"\nИтого новых: {total_new}. Всего в базе: {count_events()}")


if __name__ == "__main__":
    asyncio.run(main())
