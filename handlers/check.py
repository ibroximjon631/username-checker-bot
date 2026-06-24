"""Username tekshiruv handleri.

/check buyrug'i va oddiy matn (username) qabul qiladi.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions, Message

from config import settings
from db import storage
from locales import t
from services.checker import check_username
from utils import limits, ui

router = Router(name="check")

# Band username havolasi katta preview qilib chiqmasligi uchun
_NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


async def _do_check(message: Message, raw: str, lang: str) -> None:
    raw = raw.strip()
    if not raw:
        await message.answer(t(lang, "USAGE_CHECK"))
        return

    if message.from_user and not await limits.allow(message.from_user.id):
        await message.answer(t(lang, "LIMIT_REACHED", limit=settings.free_daily_limit))
        return

    wait = await message.answer(t(lang, "CHECKING", username=raw.lstrip("@")))
    result = await check_username(raw)

    markup = None
    if result.status == "free":
        text = t(lang, "RESULT_FREE", username=result.username)
        markup = await ui.result_markup(result.username, lang, "free")
    elif result.status == "taken":
        text = t(lang, "RESULT_TAKEN", username=result.username)
        markup = await ui.result_markup(result.username, lang, "taken", watching=False)
    elif result.status == "invalid":
        text = t(lang, "RESULT_INVALID", reason=t(lang, result.reason))
    else:
        text = t(lang, "RESULT_UNKNOWN", username=result.username)

    if result.status != "invalid" and message.from_user:
        await storage.upsert_user(message.from_user.id, message.from_user.username)
        await storage.add_history(message.from_user.id, result.username, result.status)

    await wait.edit_text(text, reply_markup=markup, link_preview_options=_NO_PREVIEW)


@router.message(Command("check"))
async def cmd_check(message: Message, lang: str) -> None:
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1] if len(parts) > 1 else ""
    await _do_check(message, arg, lang)


@router.message(F.text & ~F.text.startswith("/"))
async def plain_username(message: Message, lang: str) -> None:
    await _do_check(message, message.text or "", lang)
