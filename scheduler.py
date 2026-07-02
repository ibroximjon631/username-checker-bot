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

        result = await check_username(username, use_cache=False)

        # Faqat aniq natijaga ishonamiz (unknown'ni o'tkazib yuboramiz)
        if result.status not in ("free", "taken"):
            continue

        # "band → bo'sh" — bu qimmatli o'tish, soxta bo'lmasligi uchun
        # qayta tasdiqlaymiz. Ikkinchi tekshiruv "free" bermasa, hali
        # statusni yangilamaymiz (keyingi siklda qayta ko'riladi).
        if old_status == "taken" and result.status == "free":
            await asyncio.sleep(2.0)
            confirm = await check_username(username, use_cache=False)
            if confirm.status != "free":
                logger.info(
                    f"@{username}: 1-tekshiruv 'free', tasdiq '{confirm.status}' "
                    f"— soxta signal, xabar yuborilmadi"
                )
                continue

        await storage.update_watch_status(watch_id, result.status)

        # Band edi → endi bo'sh bo'ldi: XABAR BER!
        if old_status == "taken" and result.status == "free":
            try:
                lang = await storage.get_lang(user_id)
                await bot.send_message(
                    user_id, t(lang, "NOTIFY_FREE", username=username)
                )
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
