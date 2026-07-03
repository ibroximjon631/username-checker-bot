"""Telethon (MTProto) qatlami — username'ni aniq tekshiradi.

IXTIYORIY: .env'da API_ID/API_HASH bo'lsa yoqiladi. Bo'lmasa bot
faqat t.me bilan ishlaydi (telethon o'chiq holatda 'unknown' qaytaradi).

Birinchi marta sessiya yaratish uchun:
    python -m services.telethon_client
(telefon raqami + Telegram'dan kelgan kod so'raydi)
"""
from __future__ import annotations

import asyncio
import time

from loguru import logger

from config import settings

_client = None  # type: ignore[var-annotated]

# --- Rate-limit / FloodWait himoyasi ---
# So'rovlarni ketma-ket va bir-biridan kamida shuncha sekund oralatib yuboramiz.
# Bu FloodWait (Telegram vaqtincha cheklovi) ehtimolini keskin kamaytiradi.
_MIN_INTERVAL = 2.0
_lock = asyncio.Lock()
_last_call = 0.0
# FloodWait tushsa, shu vaqtgacha Telethon'ni ishlatmaymiz (t.me'ga tushib qolamiz).
_cooldown_until = 0.0


async def init_telethon() -> None:
    """Botstartupida chaqiriladi. Sozlanmagan bo'lsa hech narsa qilmaydi."""
    global _client
    if not settings.telethon_enabled:
        logger.info("Telethon o'chiq (API_ID/API_HASH yo'q) — faqat t.me ishlaydi.")
        return

    try:
        from telethon import TelegramClient

        _client = TelegramClient(
            settings.telethon_session, settings.api_id, settings.api_hash
        )
        await _client.connect()
        if not await _client.is_user_authorized():
            logger.warning(
                "Telethon sessiyasi avtorizatsiyalanmagan! "
                "`python -m services.telethon_client` ishga tushiring."
            )
            _client = None
            return
        logger.info("Telethon ulandi — aniq tekshiruv yoqildi.")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Telethon ishga tushmadi: {e}")
        _client = None


async def close_telethon() -> None:
    if _client is not None:
        await _client.disconnect()


def is_enabled() -> bool:
    return _client is not None


async def check_telethon(username: str) -> str:
    """Username holatini MTProto orqali aniqlaydi.

    Returns: "free" | "taken" | "unknown"

    Rate-limit: so'rovlar ketma-ket (lock) va _MIN_INTERVAL oralatib yuboriladi.
    FloodWait tushsa, _cooldown_until gacha "unknown" qaytaramiz (t.me ishlaydi).
    """
    global _last_call, _cooldown_until

    if _client is None:
        return "unknown"

    # FloodWait cooldown ichidamizmi?
    now = time.monotonic()
    if now < _cooldown_until:
        return "unknown"

    from telethon.errors import (
        FloodWaitError,
        UsernameInvalidError,
        UsernameNotOccupiedError,
    )
    from telethon.tl.functions.contacts import ResolveUsernameRequest

    async with _lock:
        # Oldingi so'rovdan beri _MIN_INTERVAL o'tishini kutamiz.
        wait = _MIN_INTERVAL - (time.monotonic() - _last_call)
        if wait > 0:
            await asyncio.sleep(wait)
        try:
            await _client(ResolveUsernameRequest(username))
            return "taken"
        except (UsernameNotOccupiedError, UsernameInvalidError):
            return "free"
        except FloodWaitError as e:
            # Telegram vaqtincha cheklov qo'ydi — shuncha sekund kutamiz.
            _cooldown_until = time.monotonic() + e.seconds + 1
            logger.warning(
                f"Telethon FloodWait {e.seconds}s ({username}) — "
                f"cooldown'ga o'tildi, shu vaqt t.me ishlatiladi"
            )
            return "unknown"
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Telethon tekshiruv xatosi ({username}): {e}")
            return "unknown"
        finally:
            _last_call = time.monotonic()


async def _interactive_login() -> None:
    """Sessiya yaratish uchun bir martalik interaktiv login."""
    from telethon import TelegramClient

    if not settings.telethon_enabled:
        print("Avval .env'da API_ID va API_HASH ni to'ldiring.")
        return

    client = TelegramClient(
        settings.telethon_session, settings.api_id, settings.api_hash
    )
    await client.start()  # telefon + kod so'raydi
    me = await client.get_me()
    print(f"✅ Muvaffaqiyatli! Kirildi: {me.first_name} (@{me.username})")
    print(f"Sessiya saqlandi: {settings.telethon_session}.session")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(_interactive_login())
