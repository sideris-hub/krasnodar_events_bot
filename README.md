# krasnodar_events_bot

Личный Telegram-бот, который собирает события Краснодара по интересам (IT/AI, спорт-актив, музыка), фильтрует через AI и присылает подборками — по запросу и пятничным дайджестом.

Подробное ТЗ, архитектура и решения — в Obsidian: `~/claude/projects/krasnodar-events-bot/`.

## стек

- Python 3.11
- aiogram 3.x (бот)
- Telethon (парсинг TG-каналов) — веха 1
- Anthropic Claude API (AI-фильтр) — веха 2
- SQLite, Docker / docker-compose

## архитектура (модульный монолит)

```
connectors → parser → dedup → ai_filter → storage → bot / scheduler
```

| Модуль | Ответственность |
|---|---|
| `app/connectors/` | тянут сырые посты из источников (старт — TG) |
| `app/parser/` | сырой пост → событие |
| `app/dedup/` | отсев дублей |
| `app/ai_filter/` | релевантность по смыслу + категория + цена |
| `app/storage/` | БД событий |
| `app/bot/` | Telegram: кнопки (pull), карточки |
| `app/scheduler/` | парсинг по расписанию + пятничный дайджест |

## запуск

```bash
cp .env.example .env      # вставить BOT_TOKEN
# локально:
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 -m app.main
# или в Docker:
docker compose up -d --build
```

## статус

- ✅ **Веха 0** — скелет: бот отвечает на `/start`, Docker, окружение
- ⬜ Веха 1 — парсинг Telegram-каналов → база
- ⬜ Веха 2 — AI-фильтр (Gemini Flash)
- ⬜ Веха 3 — кнопки (pull)
- ⬜ Веха 4 — пятничный дайджест (push)
