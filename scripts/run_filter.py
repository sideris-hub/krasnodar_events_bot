"""Прогон AI-фильтра по неклассифицированным событиям. Веха 2.

Ступень 1 (предотсев) бесплатно отсеивает не-события; ступень 2 (Gemini)
классифицирует остальное пачками (батчинг экономит запросы к API).
Запуск:  python -m scripts.run_filter
"""
import time

from app.ai_filter.classify import classify_batch, passes_prefilter
from app.storage.db import get_unclassified, init_db, set_classification

BATCH_SIZE = 8       # постов в одном запросе к Gemini
BATCH_DELAY = 5      # пауза между запросами


def main() -> None:
    init_db()
    rows = get_unclassified()
    print(f"К обработке: {len(rows)} событий")

    # ступень 1 — предотсев
    candidates = []
    skipped = 0
    for ev in rows:
        if passes_prefilter(ev):
            candidates.append(ev)
        else:
            set_classification(ev["id"], relevant=0, category=None)
            skipped += 1
    print(f"Предотсев отбросил {skipped}, на Gemini идёт {len(candidates)}")

    # ступень 2 — батчи через Gemini
    sent = relevant = 0
    for start in range(0, len(candidates), BATCH_SIZE):
        batch = candidates[start:start + BATCH_SIZE]
        try:
            results = classify_batch(batch)
        except Exception as exc:
            print(f"  батч {start}: ошибка LLM — {exc}")
            continue
        if not results:
            print(f"  батч {start}: рассинхрон ответа, пропускаю")
            continue

        for ev, res in zip(batch, results):
            is_event = bool(res.get("is_event"))
            category = res.get("category") if is_event else None
            rel = 1 if (is_event and category != "standup") else 0
            set_classification(ev["id"], relevant=rel, category=category, is_free=res.get("is_free"))
            sent += 1
            if rel:
                relevant += 1
                print(f"  ✓ [{category}] {res.get('title', '')[:70]}")
        time.sleep(BATCH_DELAY)

    print(f"\nИтого: отсеяно {skipped}, классифицировано {sent}, релевантных {relevant}.")


if __name__ == "__main__":
    main()
