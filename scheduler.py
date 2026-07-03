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
from services import telethon_client
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


async def _auto_claim_loop(bot: Bot) -> None:
    """Avto-egallash — bo'shagan username'ni darhol yangi kanal ochib egallaydi.

    Oddiy monitoringdan tezroq (autoclaim_interval_seconds) ishlaydi, chunki
    poygada birinchi bo'lish muhim. Faqat Telethon yoqilganда ishlaydi.
    """
    if not telethon_client.is_enabled():
        return
    rows = await storage.all_auto_claims()
    if not rows:
        return

    for r in rows:
        watch_id = r["id"]
        user_id = r["user_id"]
        username = r["target_username"]

        result = await check_username(username, use_cache=False)
        if result.status != "free":
            # band yoki noaniq — hali vaqti emas.
            continue

        # Bo'sh! Darhol egallaymiz (egallash o'zi ham "band"ni tekshiradi —
        # agar poygada yutqazsak, UsernameOccupied qaytadi).
        ok, info = await telethon_client.claim_via_new_channel(
            username, settings.autoclaim_channel_title
        )
        lang = await storage.get_lang(user_id)

        if ok:
            await storage.mark_claimed(watch_id)
            try:
                await bot.send_message(
                    user_id, t(lang, "NOTIFY_CLAIMED", username=username, link=info)
                )
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Egallandi xabari yuborilmadi ({user_id}): {e}")
        else:
            logger.warning(f"@{username} egallab bo'lmadi: {info}")
            # Poygada yutqazdik (boshqa birov oldi) — foydalanuvchini ogohlantiramiz.
            # (FloodWait/vaqtincha xatolarда spam qilmaymiz, keyingi siklda urinamiz.)
            if "ilib ketdi" in info:
                try:
                    await bot.send_message(
                        user_id,
                        t(lang, "NOTIFY_CLAIM_FAILED", username=username, reason=info),
                    )
                except Exception:  # noqa: BLE001
                    pass

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
    scheduler.add_job(
        _auto_claim_loop,
        trigger="interval",
        seconds=settings.autoclaim_interval_seconds,
        args=[bot],
        id="auto_claim",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler yoqildi — monitoring har {settings.check_interval_minutes} "
        f"daqiqada, auto-egallash har {settings.autoclaim_interval_seconds}s."
    )
    return scheduler
