"""Разовый импорт событий из KudaGo -> нормализация -> база. Вторая волна.

Запуск из корня проекта:  python -m scripts.fetch_kudago
Дальше классификация общим фильтром:  python -m scripts.run_filter
"""
from app.connectors.kudago import fetch_events
from app.parser.extract import extract_hints
from app.storage.db import count_events, init_db, save_event


def main() -> None:
    init_db()
    try:
        events = fetch_events()
    except Exception as exc:
        print(f"KudaGo: ошибка — {exc}")
        return

    new = 0
    for ev in events:
        ev.update(extract_hints(ev["text"]))
        if save_event(ev):
            new += 1
    print(f"KudaGo: получено {len(events)}, новых {new}. Всего в базе: {count_events()}")


if __name__ == "__main__":
    main()
