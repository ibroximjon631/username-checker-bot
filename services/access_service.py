"""Kirish nazorati — umumiy mantiq (callback va admin buyruqlari uchun).

Holatni o'zgartiradi va foydalanuvchini o'z tilida xabardor qiladi.
"""
from __future__ import annotations

from aiogram import Bot
from loguru import logger

from db import storage
from locales import DEFAULT_LANG, t


async def apply_decision(bot: Bot, target_id: int, approve: bool) -> dict | None:
    """Foydalanuvchi holatini o'zgartiradi va unga xabar yuboradi.

    Returns: {"username": ..., "status": ...} yoki None (foydalanuvchi topilmasa).
    """
    target = await storage.get_user(target_id)
    if target is None:
        return None

    new_status = "approved" if approve else "rejected"
    await storage.set_status(target_id, new_status)

    ulang = target["lang"] or DEFAULT_LANG
    notify_key = "APPROVED_NOTIFY" if approve else "REJECTED_NOTIFY"
    try:
        await bot.send_message(target_id, t(ulang, notify_key))
    except Exception as e:  # noqa: BLE001 — foydalanuvchi botni bloklagan bo'lishi mumkin
        logger.warning(f"Foydalanuvchiga ({target_id}) xabar yetmadi: {e}")

    return {"username": target["username"], "status": new_status}
