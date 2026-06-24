"""Admin tasdiqlash oqimi: tasdiqlash / rad etish tugmalari."""
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from config import settings
from db import storage
from locales import t
from services.access_service import apply_decision

router = Router(name="access")


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_id_list


async def _decide(call: CallbackQuery, bot: Bot, lang: str, approve: bool) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer(t(lang, "ADMIN_ONLY"), show_alert=True)
        return

    target_id = int(call.data.split(":", 1)[1])
    target = await storage.get_user(target_id)

    # Allaqachon hal qilingan bo'lsa (boshqa admin yoki takror bosish)
    if target is not None and target["status"] in ("approved", "rejected"):
        await call.answer(t(lang, "CB_ALREADY_HANDLED"))
        return

    await apply_decision(bot, target_id, approve)

    uname = target["username"] if target and target["username"] else "—"
    name = f"@{uname}" if uname != "—" else str(target_id)
    done_key = "ADMIN_APPROVED_DONE" if approve else "ADMIN_REJECTED_DONE"
    await call.answer(t(lang, "CB_APPROVED" if approve else "CB_REJECTED"))
    await call.message.edit_text(t(lang, done_key, name=name, uid=target_id))
    logger.info(f"Admin {call.from_user.id} -> {'approved' if approve else 'rejected'}: {target_id}")


@router.callback_query(F.data.startswith("approve:"))
async def cb_approve(call: CallbackQuery, bot: Bot, lang: str) -> None:
    await _decide(call, bot, lang, approve=True)


@router.callback_query(F.data.startswith("reject:"))
async def cb_reject(call: CallbackQuery, bot: Bot, lang: str) -> None:
    await _decide(call, bot, lang, approve=False)
