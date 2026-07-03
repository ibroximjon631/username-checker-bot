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


async def _get_holding_channel() -> tuple[int, int] | None:
    """"Tayyor" kanalni qaytaradi (saqlanganini yoki yangisini ochib).

    Kanal ochib-o'chirish churn'ini yo'q qiladi: bitta kanal ko'p urinishда
    qayta ishlatiladi, faqat egallash muvaffaqiyatli bo'lganда "iste'mol" qilinadi.
    """
    raw = await storage.get_state("holding_channel")
    if raw:
        try:
            cid, chash = raw.split(":")
            return int(cid), int(chash)
        except ValueError:
            pass
    created = await telethon_client.create_holding_channel(
        settings.autoclaim_channel_title
    )
    if created:
        await storage.set_state("holding_channel", f"{created[0]}:{created[1]}")
    return created


async def _auto_claim_loop(bot: Bot) -> None:
    """Avto-egallash — bo'shagan username'ni tayyor kanalga o'rnatib egallaydi.

    Oddiy monitoringdan tezroq (autoclaim_interval_seconds) ishlaydi. Faqat
    Telethon yoqilgan va u ANIQ 'free' deganда harakat qiladi (t.me'ga ishonmaydi).
    """
    if not telethon_client.is_enabled():
        return
    rows = await storage.all_auto_claims()
    if not rows:
        return
    holding = await _get_holding_channel()
    if holding is None:
        return
    cid, chash = holding

    for r in rows:
        watch_id = r["id"]
        user_id = r["user_id"]
        username = r["target_username"]
        notified = r["claim_notified"]

        # Egallash — muhim/qaytmas amal. Shuning uchun faqat Telethon (aniq)
        # 'free' desagina urinamiz; t.me throttle 'free'siga ishonmaymiz.
        tele = await telethon_client.check_telethon(username)
        if tele != "free":
            # Yana band bo'lsa, keyingi "bo'sh" epizodда qayta xabar bera olamiz.
            if tele == "taken" and notified:
                await storage.set_claim_notified(watch_id, 0)
            continue

        ok, info = await telethon_client.claim_username_on(cid, chash, username)
        lang = await storage.get_lang(user_id)

        if ok:
            # Egallandi — yozuvni ro'yxatdan butunlay o'chiramiz (qolib ketmasin).
            await storage.remove_watch_by_id(watch_id)
            try:
                await bot.send_message(
                    user_id, t(lang, "NOTIFY_CLAIMED", username=username, link=info)
                )
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Egallandi xabari yuborilmadi ({user_id}): {e}")
            # Kanal iste'mol qilindi — keyingisini tayyorlaymiz.
            await storage.del_state("holding_channel")
            nxt = await _get_holding_channel()
            if nxt is None:
                break
            cid, chash = nxt
        elif info == "occupied":
            # Bo'sh ko'rinadi, lekin hali egallab bo'lmaydi — odatда Telegram
            # bo'shatilgandan keyin ~25 daqiqa rezervda ushlaydi. Jimgina qayta
            # urinamiz (kanal saqlanadi), foydalanuvchiga BIR marta xabar beramiz.
            logger.info(f"@{username}: bo'sh ko'rinadi, hali egallab bo'lmadi (rezerv)")
            if not notified:
                try:
                    await bot.send_message(
                        user_id, t(lang, "NOTIFY_CLAIM_WAIT", username=username)
                    )
                except Exception:  # noqa: BLE001
                    pass
                await storage.set_claim_notified(watch_id, 1)
        else:
            # flood / boshqa vaqtincha xato — jim, keyingi siklda urinamiz.
            logger.warning(f"@{username} egallab bo'lmadi: {info}")

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
