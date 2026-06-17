"""Коннектор к KudaGo через официальное публичное API. Вторая волна источников.

Без скрапинга: kudago.com/public-api отдаёт структурированный JSON по городу.
Берём только актуальные (будущие) события. Приводим к тому же сырому формату,
что и TG-посты, чтобы они шли через общую трубу (нормализация → дедуп → AI-фильтр).

Контракт: fetch_events() -> list[raw_post].
"""
import datetime as dt
import re
import time

import requests

API_URL = "https://kudago.com/public-api/v1.4/events/"
LOCATION = "krd"
FIELDS = "id,title,description,dates,place,price,is_free,site_url,categories"
USER_AGENT = "Mozilla/5.0 (compatible; krasnodar-events-bot/0.1)"

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text or "").strip()


def _nearest_date_iso(dates: list[dict]) -> str | None:
    """Ближайшая дата начала события (ISO) или None для бессрочных/битых."""
    starts = [d.get("start") for d in (dates or []) if isinstance(d.get("start"), int)]
    sane = [s for s in starts if 0 < s < 4102444800]  # отсекаем плейсхолдеры
    if not sane:
        return None
    return dt.datetime.fromtimestamp(min(sane), tz=dt.timezone.utc).date().isoformat()


def _to_raw(ev: dict) -> dict:
    place = ev.get("place") or {}
    date_iso = _nearest_date_iso(ev.get("dates"))

    parts = [ev.get("title", "")]
    desc = _strip_html(ev.get("description"))
    if desc:
        parts.append(desc)
    if place.get("title"):
        parts.append(f"Место: {place['title']}, {place.get('address', '')}".strip(", "))
    if date_iso:
        parts.append(f"Дата: {date_iso}")
    if ev.get("is_free"):
        parts.append("Вход бесплатный")
    elif ev.get("price"):
        parts.append(f"Цена: {ev['price']}")
    if ev.get("site_url"):
        parts.append(ev["site_url"])

    return {
        "source": "kudago",
        "msg_id": ev["id"],
        "posted_at": date_iso,
        "text": "\n".join(p for p in parts if p),
    }


def fetch_events(limit: int = 100) -> list[dict]:
    """Актуальные события Краснодара из KudaGo как список сырых записей."""
    params = {
        "location": LOCATION,
        "actual_since": int(time.time()),
        "fields": FIELDS,
        "expand": "place",
        "page_size": 100,
        "order_by": "dates",
    }
    headers = {"User-Agent": USER_AGENT}

    posts: list[dict] = []
    url: str | None = API_URL
    first = True
    while url and len(posts) < limit:
        resp = requests.get(url, params=params if first else None, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for ev in data.get("results", []):
            posts.append(_to_raw(ev))
        url = data.get("next")
        first = False

    return posts[:limit]
