"""Двухступенчатый фильтр событий. Веха 2.

Ступень 1 (бесплатно): предотсев — постов без признаков события не гоняем через LLM.
Ступень 2 (Gemini): понимание по смыслу — событие/нет, категория, бесплатно/нет.
"""
import re

from app.ai_filter.gemini import generate_json

CATEGORIES = ("it_ai", "sport", "music", "other", "standup")

EVENT_KEYWORDS = re.compile(
    r"(митап|meetup|лекци|концерт|выставк|фестивал|мастер[\s-]?класс|воркшоп|workshop"
    r"|хакатон|забег|марафон|турнир|спектакл|показ|премьер|вечеринк|afterparty|афтерпати"
    r"|регистраци|билет|вход|расписани|анонс|приглаша|встреч|tedx?|конференци|форум)",
    re.IGNORECASE,
)

RULES = """Правила:
- is_event=true только если это анонс конкретного мероприятия (есть что посетить), а не новость, реклама товара/услуги, мнение или подборка ссылок.
- category: it_ai — айти/технологии/ИИ/разработка; sport — спорт, забеги, марафоны, ролики, активности; music — концерты/живая музыка; standup — стендап/комедия; other — всё прочее.
- is_free — вход бесплатный (true/false).
- title — краткое название события до 80 символов."""

BATCH_PROMPT = """Тебе дан список постов из Telegram-каналов Краснодара для афиши событий.
Классифицируй КАЖДЫЙ пост. Верни СТРОГО JSON-массив той же длины и в том же порядке,
по одному объекту на пост:
{{"is_event": bool, "category": "it_ai"|"sport"|"music"|"other"|"standup", "is_free": bool, "title": "строка"}}

{rules}

Посты:
{posts}"""


def passes_prefilter(ev: dict) -> bool:
    """Ступень 1: есть ли признаки события (дёшево, без LLM)."""
    if ev.get("date_hint") or ev.get("price_hint"):
        return True
    return bool(EVENT_KEYWORDS.search(ev.get("text") or ""))


def classify_batch(events: list[dict]) -> list[dict]:
    """Ступень 2: классификация пачки постов одним запросом к Gemini.

    Возвращает список той же длины (по индексам входа); при рассинхроне —
    пустой список (события останутся неклассифицированными и обработаются позже).
    """
    posts = "\n\n".join(
        f"[{i + 1}]\n\"\"\"{(ev.get('text') or '')[:1200]}\"\"\""
        for i, ev in enumerate(events)
    )
    result = generate_json(BATCH_PROMPT.format(rules=RULES, posts=posts))
    if isinstance(result, list) and len(result) == len(events):
        return result
    return []
