"""Хранилище событий (SQLite). Веха 1.

Дедупликация на двух уровнях:
  - UNIQUE(source, msg_id) — один и тот же пост при повторном парсинге не задвоится;
  - content_hash — один и тот же текст из разных каналов считается дублем.

Поля relevant/category заполняет AI-фильтр на вехе 2 (пока NULL).
"""
import json
import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "events.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            source       TEXT    NOT NULL,
            msg_id       INTEGER NOT NULL,
            posted_at    TEXT,
            text         TEXT,
            urls         TEXT,            -- json-список ссылок
            price_hint   TEXT,            -- 'free' | число | NULL
            date_hint    TEXT,            -- найденная дата события | NULL
            content_hash TEXT,            -- для кросс-канального дедупа
            category     TEXT,            -- заполняет AI (веха 2)
            relevant     INTEGER,         -- 1/0/NULL, заполняет AI (веха 2)
            fetched_at   TEXT DEFAULT (datetime('now')),
            UNIQUE(source, msg_id)
        );
        CREATE INDEX IF NOT EXISTS idx_events_hash   ON events(content_hash);
        CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
        """
    )
    conn.commit()
    conn.close()


def save_event(ev: dict) -> bool:
    """Сохранить событие. Возвращает True, если вставлено, False — если дубль."""
    conn = get_conn()
    try:
        chash = ev.get("content_hash")
        if chash:
            dup = conn.execute(
                "SELECT 1 FROM events WHERE content_hash = ? LIMIT 1", (chash,)
            ).fetchone()
            if dup:
                return False
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO events
                (source, msg_id, posted_at, text, urls, price_hint, date_hint, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ev["source"],
                ev["msg_id"],
                ev.get("posted_at"),
                ev.get("text"),
                json.dumps(ev.get("urls", []), ensure_ascii=False),
                ev.get("price_hint"),
                ev.get("date_hint"),
                chash,
            ),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def count_events() -> int:
    conn = get_conn()
    try:
        return conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    finally:
        conn.close()


def get_unclassified(limit: int = 200) -> list[dict]:
    """События, которые ещё не прошли AI-фильтр (relevant IS NULL)."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM events WHERE relevant IS NULL ORDER BY id LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_classification(
    event_id: int, relevant: int, category: str | None = None, is_free: bool | None = None
) -> None:
    """Записать результат AI-фильтра. is_free=True проставляет price_hint='free'."""
    conn = get_conn()
    try:
        if is_free is True:
            conn.execute(
                "UPDATE events SET relevant = ?, category = ?, price_hint = 'free' WHERE id = ?",
                (relevant, category, event_id),
            )
        else:
            conn.execute(
                "UPDATE events SET relevant = ?, category = ? WHERE id = ?",
                (relevant, category, event_id),
            )
        conn.commit()
    finally:
        conn.close()
