"""Лёгкая нормализация поста -> подсказки для события. Веха 1.

Это НЕ полноценное извлечение события — оно делается AI на вехе 2.
Здесь дёшево и без LLM достаём то, что ловится регулярками: ссылки, цену,
дату-кандидат — и считаем content_hash для дедупа.
"""
import hashlib
import re

URL_RE = re.compile(r"https?://\S+")
PRICE_RE = re.compile(r"(\d[\d\s]{0,6})\s*(?:₽|руб|р\.)", re.IGNORECASE)
FREE_RE = re.compile(
    r"(бесплатн|вход свободн|free\b|0\s*₽)", re.IGNORECASE
)
DATE_RE = re.compile(
    r"(\d{1,2}\s?(?:янв|фев|мар|апр|ма[йя]|июн|июл|авг|сен|окт|ноя|дек)[а-я]*"
    r"|\d{1,2}\.\d{1,2}(?:\.\d{2,4})?)",
    re.IGNORECASE,
)


def extract_hints(text: str) -> dict:
    text = text or ""
    urls = URL_RE.findall(text)

    if FREE_RE.search(text):
        price_hint = "free"
    else:
        m = PRICE_RE.search(text)
        price_hint = m.group(1).replace(" ", "") if m else None

    dm = DATE_RE.search(text)
    date_hint = dm.group(1) if dm else None

    normalized = re.sub(r"\s+", " ", text).strip().lower()
    content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    return {
        "urls": urls,
        "price_hint": price_hint,
        "date_hint": date_hint,
        "content_hash": content_hash,
    }
