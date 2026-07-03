"""Monitoring scheduler — kuzatuvdagi username'larni davriy tekshiradi.

Band username bo'shasa, kuzatuvchiga avtomatik xabar yuboradi.
"""
import asyncio

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from config import settings
from db import storage
from locales import t
from services.checker import check_username

# "band → bo'sh" xabari yuborilishidan oldin username shuncha marta KETMA-KET
# (har sikl = check_interval_minutes) "bo'sh" bo'lishi kerak. Bitta throttle/xato
# blip 30 daqiqalik oraliqda takrorlanmaydi — shu bilan soxta xabar oldini olamiz.
REQUIRED_FREE_CONFIRMATIONS = 2


async def _check_watchlist(bot: Bot) -> None:
    """Barcha kuzatuv yozuvlarini ko'rib chiqadi."""
    rows = await storage.all_watches()
    if not rows:
        return
    logger.info(f"Monitoring: {len(rows)} ta username tekshirilmoqda…")

    for r in rows:
        watch_id = r["id"]
        user_id = r["user_id"]
        username = r["target_username"]
        old_status = r["status"]
        streak = r["free_streak"]

        result = await check_username(username, use_cache=False)

        # Aniq emas (unknown/invalid) — hech narsani o'zgartirmaymiz.
        # Sanoqni ham nolga tushirmaymiz: throttle blip streak'ni buzmasin.
        if result.status not in ("free", "taken"):
            await asyncio.sleep(1.0)
            continue

        # Band deb o'qildi — sanoqni nolga tushiramiz.
        if result.status == "taken":
            if old_status != "taken" or streak != 0:
                await storage.update_watch_status(watch_id, "taken", free_streak=0)
            await asyncio.sleep(1.0)
            continue

        # Bu yerdan result.status == "free"
        if old_status == "free":
            # Allaqachon bo'sh deb belgilangan — qayta xabar yo'q.
            await asyncio.sleep(1.0)
            continue

        # old_status == "taken", hozir "free" o'qildi — nomzod o'tish.
        new_streak = streak + 1
        if new_streak < REQUIRED_FREE_CONFIRMATIONS:
            # Hali tasdiqlanmadi — statusni "taken"da qoldiramiz, faqat sanoqni oshiramiz.
            await storage.set_free_streak(watch_id, new_streak)
            logger.info(
                f"@{username}: 'bo'sh' tasdig'i {new_streak}/"
                f"{REQUIRED_FREE_CONFIRMATIONS} — hali xabar yo'q"
            )
            await asyncio.sleep(1.0)
            continue

        # Tasdiqlandi — endi bo'sh deb belgilaymiz va XABAR BERAMIZ.
        await storage.update_watch_status(watch_id, "free", free_streak=0)
        try:
            lang = await storage.get_lang(user_id)
            await bot.send_message(user_id, t(lang, "NOTIFY_FREE", username=username))
            logger.info(f"🎉 Xabar yuborildi: {user_id} -> @{username} bo'shadi")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Xabar yuborilmadi ({user_id}): {e}")

        # Flood-limitdan saqlanish uchun kichik pauza
        await asyncio.sleep(1.0)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _check_watchlist,
        trigger="interval",
        minutes=settings.check_interval_minutes,
        args=[bot],
        id="watchlist_monitor",
        max_instances=1,          # oldingisi tugamasa, yangisi boshlanmaydi
        coalesce=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler yoqildi — har {settings.check_interval_minutes} daqiqada tekshiradi."
    )
    return scheduler
