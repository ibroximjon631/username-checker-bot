"""Global xato ushlagich — kutilmagan xatolarni adminlarga yuboradi.

Bir xil xato qayta-qayta bo'lsa, spam bo'lmasligi uchun throttling bor.
"""
from __future__ import annotations

import html
import time
import traceback

from aiogram import Bot, Router
from aiogram.types import ErrorEvent
from loguru import logger

from config import settings

router = Router(name="errors")

# Bir xil xatoni qayta yubormaslik uchun: error_key -> oxirgi yuborilgan vaqt
_last_sent: dict[str, float] = {}
THROTTLE_SECONDS = 120.0


def _who(event: ErrorEvent) -> str:
    """Xato qaysi foydalanuvchi/kontekstdan kelganini aniqlaydi."""
    upd = event.update
    if upd is None:
        return "—"
    obj = upd.message or upd.callback_query
    if obj and obj.from_user:
        u = obj.from_user
        uname = f"@{u.username}" if u.username else "—"
        return f"{u.full_name} ({uname}, <code>{u.id}</code>)"
    return "—"


@router.errors()
async def on_error(event: ErrorEvent, bot: Bot) -> None:
    exc = event.exception
    logger.exception(f"Kutilmagan xato: {exc!r}")

    err_key = f"{type(exc).__name__}:{exc}"
    now = time.time()
    last = _last_sent.get(err_key, 0.0)
    if now - last < THROTTLE_SECONDS:
        return  # yaqinda yuborilgan — spam qilmaymiz
    _last_sent[err_key] = now

    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    tb_tail = tb[-1500:]  # Telegram xabar limiti uchun oxirgi qismi

    text = (
        "⚠️ <b>Bot xatosi</b>\n\n"
        f"👤 {_who(event)}\n"
        f"❗️ <code>{html.escape(type(exc).__name__)}: {html.escape(str(exc))}</code>\n\n"
        f"<pre>{html.escape(tb_tail)}</pre>"
    )

    for admin_id in settings.admin_id_list:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Xato xabarini adminga ({admin_id}) yuborib bo'lmadi: {e}")
