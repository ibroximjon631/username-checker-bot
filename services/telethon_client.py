"""Telethon (MTProto) qatlami — username'ni aniq tekshiradi.

IXTIYORIY: .env'da API_ID/API_HASH bo'lsa yoqiladi. Bo'lmasa bot
faqat t.me bilan ishlaydi (telethon o'chiq holatda 'unknown' qaytaradi).

Birinchi marta sessiya yaratish uchun:
    python -m services.telethon_client
(telefon raqami + Telegram'dan kelgan kod so'raydi)
"""
from __future__ import annotations

import asyncio

from loguru import logger

from config import settings

_client = None  # type: ignore[var-annotated]


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
    """
    if _client is None:
        return "unknown"
    try:
        from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError
        from telethon.tl.functions.contacts import ResolveUsernameRequest

        try:
            await _client(ResolveUsernameRequest(username))
            return "taken"
        except (UsernameNotOccupiedError, UsernameInvalidError):
            return "free"
    except Exception as e:  # noqa: BLE001
        # FloodWait va boshqa xatolar — noaniq deb qaytaramiz
        logger.warning(f"Telethon tekshiruv xatosi ({username}): {e}")
        return "unknown"


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
