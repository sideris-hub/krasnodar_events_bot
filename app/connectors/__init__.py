"""Коннекторы к источникам событий.

Веха 1: Telegram-каналы (через Telethon, user-сессия).
Вторая волна: VK-сообщества, сайты-афиши.

Контракт коннектора: fetch() -> list[raw_post]. Новый источник = новый файл,
ядро пайплайна не меняется.

Активный коннектор вехи 1 — telegram.py (Telethon, user-сессия).
"""

# каналы из ТЗ (веха 1)
CHANNELS = [
    "krdpike",
    "insite_krd",
    "zatsepi_coffee",
    "yandex_cup",
]
