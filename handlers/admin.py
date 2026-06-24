"""Admin handlerlari: /stats, /broadcast, /users, /pending, /approve, /revoke.

Faqat .env'dagi ADMIN_IDS ro'yxatidagilar foydalana oladi.
"""
import asyncio

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

import keyboards
from config import settings
from db import storage
from locales import t
from services.access_service import apply_decision

router = Router(name="admin")


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_list


@router.message(Command("stats"))
async def cmd_stats(message: Message, lang: str) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer(t(lang, "ADMIN_ONLY"))
        return
    s = await storage.stats()
    await message.answer(t(lang, "STATS", **s))


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot, lang: str) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer(t(lang, "ADMIN_ONLY"))
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(t(lang, "BROADCAST_USAGE"))
        return

    text = parts[1]
    user_ids = await storage.all_user_ids()
    status = await message.answer(t(lang, "BROADCAST_START", total=len(user_ids)))

    ok = failed = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
            ok += 1
        except Exception as e:  # noqa: BLE001
            failed += 1
            logger.debug(f"Broadcast yetib bormadi ({uid}): {e}")
        await asyncio.sleep(0.05)

    await status.edit_text(
        t(lang, "BROADCAST_DONE", ok=ok, total=len(user_ids), failed=failed)
    )


@router.message(Command("users"))
async def cmd_users(message: Message, lang: str) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer(t(lang, "ADMIN_ONLY"))
        return
    counts = await storage.status_counts()
    await message.answer(t(lang, "USERS_STATS", **counts))


@router.message(Command("pending"))
async def cmd_pending(message: Message, lang: str) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer(t(lang, "ADMIN_ONLY"))
        return
    rows = await storage.list_by_status("pending", limit=20)
    if not rows:
        await message.answer(t(lang, "PENDING_EMPTY"))
        return

    await message.answer(t(lang, "PENDING_HEADER", count=len(rows)))
    for r in rows:
        name = f"@{r['username']}" if r["username"] else "—"
        await message.answer(
            t(lang, "PENDING_ITEM", name=name, uid=r["id"]),
            reply_markup=keyboards.approve_keyboard(r["id"], lang),
        )


@router.message(Command("approve"))
async def cmd_approve(message: Message, bot: Bot, lang: str) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer(t(lang, "ADMIN_ONLY"))
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.answer(t(lang, "APPROVE_USAGE"))
        return
    uid = int(parts[1].strip())
    result = await apply_decision(bot, uid, approve=True)
    if result is None:
        await message.answer(t(lang, "USER_NOT_FOUND", uid=uid))
    else:
        await message.answer(t(lang, "APPROVED_OK", uid=uid))


@router.message(Command("revoke"))
async def cmd_revoke(message: Message, bot: Bot, lang: str) -> None:
    if not message.from_user or not _is_admin(message.from_user.id):
        await message.answer(t(lang, "ADMIN_ONLY"))
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.answer(t(lang, "REVOKE_USAGE"))
        return
    uid = int(parts[1].strip())
    result = await apply_decision(bot, uid, approve=False)
    if result is None:
        await message.answer(t(lang, "USER_NOT_FOUND", uid=uid))
    else:
        await message.answer(t(lang, "REVOKED_OK", uid=uid))
