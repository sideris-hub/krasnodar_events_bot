"""Минимальный клиент Gemini API (REST, stdlib). Веха 2.

Без внешних SDK: POST на generateContent, просим строгий JSON.
Ретрай на 429 (превышение rate limit бесплатного тарифа).
"""
import json
import time
import urllib.error
import urllib.request

from app.config import GEMINI_API_KEY

MODEL = "gemini-2.5-flash-lite"  # отдельная квота + дешевле под классификацию
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def generate_json(prompt: str, timeout: int = 30, retries: int = 3):
    """Отправить промпт, вернуть распарсенный JSON (объект или массив)."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY не задан в .env")

    body = json.dumps(
        {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{ENDPOINT}?key={GEMINI_API_KEY}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as exc:
            # 429 — rate limit, 500/503 — временная перегрузка: ретраим с бэкоффом
            if exc.code in (429, 500, 503) and attempt < retries - 1:
                # 429 — ждём полную минуту (per-minute окно сбрасывается); 5xx — короче
                wait = 35 * (attempt + 1) if exc.code == 429 else 8 * (attempt + 1)
                print(f"  Gemini {exc.code}, жду {wait}с и повторяю...")
                time.sleep(wait)
                continue
            raise

    raise RuntimeError("Gemini: исчерпаны попытки")
