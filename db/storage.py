"""SQLite ma'lumotlar qatlami (aiosqlite).

Jadvallar: users, watchlist, history.
Bitta global ulanish — bot startupida ochiladi.
"""
from __future__ import annotations

import aiosqlite
from loguru import logger

from config import settings

_db: aiosqlite.Connection | None = None


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT,
    lang        TEXT DEFAULT 'uz',
    status      TEXT DEFAULT 'pending',
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS watchlist (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    target_username TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'taken',
    free_streak     INTEGER NOT NULL DEFAULT 0,
    auto_claim      INTEGER NOT NULL DEFAULT 0,
    added_at        TEXT DEFAULT (datetime('now')),
    last_checked    TEXT,
    UNIQUE(user_id, target_username)
);

CREATE TABLE IF NOT EXISTS history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    username    TEXT NOT NULL,
    result      TEXT NOT NULL,
    checked_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS daily_usage (
    user_id     INTEGER NOT NULL,
    day         TEXT NOT NULL,
    count       INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day)
);

CREATE TABLE IF NOT EXISTS bot_state (
    key    TEXT PRIMARY KEY,
    value  TEXT
);
"""


async def init_db() -> None:
    global _db
    _db = await aiosqlite.connect(settings.db_path)
    _db.row_factory = aiosqlite.Row
    await _db.executescript(SCHEMA)
    await _migrate()
    await _db.commit()
    logger.info(f"DB tayyor: {settings.db_path}")


async def _migrate() -> None:
    """Eski bazalarga yangi ustunlarni qo'shadi (xavfsiz)."""
    cur = await _db.execute("PRAGMA table_info(users)")
    cols = {row[1] for row in await cur.fetchall()}
    if "lang" not in cols:
        await _db.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'uz'")
        logger.info("Migratsiya: users.lang ustuni qo'shildi")
    if "status" not in cols:
        await _db.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending'")
        # Eski foydalanuvchilar (gate paydo bo'lishidan oldingilar) — tasdiqlangan
        await _db.execute("UPDATE users SET status = 'approved'")
        logger.info("Migratsiya: users.status ustuni qo'shildi (eskilar approved)")

    cur = await _db.execute("PRAGMA table_info(watchlist)")
    wcols = {row[1] for row in await cur.fetchall()}
    if "free_streak" not in wcols:
        await _db.execute(
            "ALTER TABLE watchlist ADD COLUMN free_streak INTEGER NOT NULL DEFAULT 0"
        )
        logger.info("Migratsiya: watchlist.free_streak ustuni qo'shildi")
    if "auto_claim" not in wcols:
        await _db.execute(
            "ALTER TABLE watchlist ADD COLUMN auto_claim INTEGER NOT NULL DEFAULT 0"
        )
        logger.info("Migratsiya: watchlist.auto_claim ustuni qo'shildi")
    if "claim_notified" not in wcols:
        await _db.execute(
            "ALTER TABLE watchlist ADD COLUMN claim_notified INTEGER NOT NULL DEFAULT 0"
        )
        logger.info("Migratsiya: watchlist.claim_notified ustuni qo'shildi")


async def close_db() -> None:
    if _db is not None:
        await _db.close()


def _conn() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("DB ishga tushmagan. Avval init_db() chaqiring.")
    return _db


# ---------- users ----------

async def upsert_user(user_id: int, username: str | None) -> None:
    await _conn().execute(
        "INSERT INTO users (id, username) VALUES (?, ?) "
        "ON CONFLICT(id) DO UPDATE SET username = excluded.username",
        (user_id, username),
    )
    await _conn().commit()


async def get_lang(user_id: int) -> str | None:
    cur = await _conn().execute("SELECT lang FROM users WHERE id = ?", (user_id,))
    row = await cur.fetchone()
    return row["lang"] if row else None


async def set_lang(user_id: int, lang: str) -> None:
    await _conn().execute(
        "INSERT INTO users (id, lang) VALUES (?, ?) "
        "ON CONFLICT(id) DO UPDATE SET lang = excluded.lang",
        (user_id, lang),
    )
    await _conn().commit()


async def get_status(user_id: int) -> str | None:
    """Foydalanuvchi holati: pending | approved | rejected. Yangi bo'lsa None."""
    cur = await _conn().execute("SELECT status FROM users WHERE id = ?", (user_id,))
    row = await cur.fetchone()
    return row["status"] if row else None


async def set_status(user_id: int, status: str) -> None:
    await _conn().execute(
        "UPDATE users SET status = ? WHERE id = ?", (status, user_id)
    )
    await _conn().commit()


async def get_user(user_id: int) -> aiosqlite.Row | None:
    cur = await _conn().execute(
        "SELECT id, username, lang, status FROM users WHERE id = ?", (user_id,)
    )
    return await cur.fetchone()


# ---------- watchlist ----------

async def add_watch(user_id: int, target: str, status: str) -> bool:
    """Kuzatuvga qo'shadi. Allaqachon bor bo'lsa False qaytaradi."""
    try:
        await _conn().execute(
            "INSERT INTO watchlist (user_id, target_username, status) VALUES (?, ?, ?)",
            (user_id, target, status),
        )
        await _conn().commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def remove_watch(user_id: int, target: str) -> bool:
    cur = await _conn().execute(
        "DELETE FROM watchlist WHERE user_id = ? AND target_username = ?",
        (user_id, target),
    )
    await _conn().commit()
    return cur.rowcount > 0


async def list_watch(user_id: int) -> list[aiosqlite.Row]:
    cur = await _conn().execute(
        "SELECT target_username, status, auto_claim FROM watchlist "
        "WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,),
    )
    return await cur.fetchall()


async def add_auto_claim(user_id: int, target: str, status: str) -> str:
    """Username'ni avto-egallashga qo'shadi/yoqadi.

    Returns: 'added' (yangi) | 'enabled' (mavjud edi, yoqildi) | 'already'.
    """
    try:
        await _conn().execute(
            "INSERT INTO watchlist (user_id, target_username, status, auto_claim) "
            "VALUES (?, ?, ?, 1)",
            (user_id, target, status),
        )
        await _conn().commit()
        return "added"
    except aiosqlite.IntegrityError:
        cur = await _conn().execute(
            "SELECT auto_claim FROM watchlist "
            "WHERE user_id = ? AND target_username = ?",
            (user_id, target),
        )
        row = await cur.fetchone()
        if row and row["auto_claim"]:
            return "already"
        await _conn().execute(
            "UPDATE watchlist SET auto_claim = 1 "
            "WHERE user_id = ? AND target_username = ?",
            (user_id, target),
        )
        await _conn().commit()
        return "enabled"


async def all_auto_claims() -> list[aiosqlite.Row]:
    """Scheduler uchun — avto-egallash yoqilgan, hali egallanmagan yozuvlar."""
    cur = await _conn().execute(
        "SELECT id, user_id, target_username, status, claim_notified FROM watchlist "
        "WHERE auto_claim = 1 AND status != 'claimed'"
    )
    return await cur.fetchall()


async def remove_watch_by_id(watch_id: int) -> None:
    """Egallangach yozuvni butunlay o'chiradi — ro'yxatda qolmasin."""
    await _conn().execute("DELETE FROM watchlist WHERE id = ?", (watch_id,))
    await _conn().commit()


async def set_claim_notified(watch_id: int, value: int) -> None:
    """'Egallab bo'lmadi' xabari bir marta yuborilishi uchun bayroq."""
    await _conn().execute(
        "UPDATE watchlist SET claim_notified = ? WHERE id = ?", (value, watch_id)
    )
    await _conn().commit()


# ---------- bot_state (kalit-qiymat) ----------

async def get_state(key: str) -> str | None:
    cur = await _conn().execute("SELECT value FROM bot_state WHERE key = ?", (key,))
    row = await cur.fetchone()
    return row["value"] if row else None


async def set_state(key: str, value: str) -> None:
    await _conn().execute(
        "INSERT INTO bot_state (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    await _conn().commit()


async def del_state(key: str) -> None:
    await _conn().execute("DELETE FROM bot_state WHERE key = ?", (key,))
    await _conn().commit()


async def all_watches() -> list[aiosqlite.Row]:
    """Monitoring uchun — faqat ODDIY kuzatuvlar (auto-egallashdagilar emas).

    Auto-egallash yozuvlarini alohida loop (all_auto_claims) boshqaradi;
    ular monitoringning 'bo'shadi, qo'lda oling' xabarini olmasligi kerak.
    """
    cur = await _conn().execute(
        "SELECT id, user_id, target_username, status, free_streak FROM watchlist "
        "WHERE auto_claim = 0"
    )
    return await cur.fetchall()


async def update_watch_status(watch_id: int, status: str, free_streak: int = 0) -> None:
    await _conn().execute(
        "UPDATE watchlist SET status = ?, free_streak = ?, "
        "last_checked = datetime('now') WHERE id = ?",
        (status, free_streak, watch_id),
    )
    await _conn().commit()


async def set_free_streak(watch_id: int, free_streak: int) -> None:
    """Statusni o'zgartirmay, faqat 'bo'sh' tasdiq sanog'ini yangilaydi."""
    await _conn().execute(
        "UPDATE watchlist SET free_streak = ?, last_checked = datetime('now') "
        "WHERE id = ?",
        (free_streak, watch_id),
    )
    await _conn().commit()


async def count_watches(user_id: int) -> int:
    cur = await _conn().execute(
        "SELECT COUNT(*) AS c FROM watchlist WHERE user_id = ?", (user_id,)
    )
    row = await cur.fetchone()
    return row["c"] if row else 0


# ---------- history ----------

async def add_history(user_id: int, username: str, result: str) -> None:
    await _conn().execute(
        "INSERT INTO history (user_id, username, result) VALUES (?, ?, ?)",
        (user_id, username, result),
    )
    await _conn().commit()


async def recent_history(user_id: int, limit: int = 10) -> list[aiosqlite.Row]:
    cur = await _conn().execute(
        "SELECT username, result, checked_at FROM history "
        "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    return await cur.fetchall()


# ---------- daily_usage (kunlik limit) ----------

async def get_usage_today(user_id: int) -> int:
    cur = await _conn().execute(
        "SELECT count FROM daily_usage WHERE user_id = ? AND day = date('now')",
        (user_id,),
    )
    row = await cur.fetchone()
    return row["count"] if row else 0


async def bump_usage_today(user_id: int) -> None:
    await _conn().execute(
        "INSERT INTO daily_usage (user_id, day, count) VALUES (?, date('now'), 1) "
        "ON CONFLICT(user_id, day) DO UPDATE SET count = count + 1",
        (user_id,),
    )
    await _conn().commit()


# ---------- admin statistika ----------

async def stats() -> dict[str, int]:
    async def _scalar(sql: str) -> int:
        cur = await _conn().execute(sql)
        row = await cur.fetchone()
        return row[0] if row and row[0] is not None else 0

    return {
        "users": await _scalar("SELECT COUNT(*) FROM users"),
        "watches": await _scalar("SELECT COUNT(*) FROM watchlist"),
        "checks_total": await _scalar("SELECT COUNT(*) FROM history"),
        "checks_today": await _scalar(
            "SELECT COALESCE(SUM(count),0) FROM daily_usage WHERE day = date('now')"
        ),
        "active_today": await _scalar(
            "SELECT COUNT(*) FROM daily_usage WHERE day = date('now')"
        ),
    }


async def all_user_ids() -> list[int]:
    """Broadcast uchun — barcha foydalanuvchi ID'lari."""
    cur = await _conn().execute("SELECT id FROM users")
    rows = await cur.fetchall()
    return [r[0] for r in rows]


async def status_counts() -> dict[str, int]:
    """Holat bo'yicha foydalanuvchilar soni."""
    cur = await _conn().execute(
        "SELECT status, COUNT(*) AS c FROM users GROUP BY status"
    )
    rows = await cur.fetchall()
    out = {"approved": 0, "pending": 0, "rejected": 0}
    for r in rows:
        out[r["status"]] = r["c"]
    return out


async def list_by_status(status: str, limit: int = 20) -> list[aiosqlite.Row]:
    cur = await _conn().execute(
        "SELECT id, username, lang FROM users WHERE status = ? "
        "ORDER BY created_at DESC LIMIT ?",
        (status, limit),
    )
    return await cur.fetchall()
