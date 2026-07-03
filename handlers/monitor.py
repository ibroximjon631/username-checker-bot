"""Monitoring (watchlist) handlerlari: /watch, /unwatch, /list, /history."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message

from db import storage
from locales import t
from services import validator
from services.checker import check_username
from utils import ui

router = Router(name="monitor")

_NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def _link(username: str) -> str:
    return f'<a href="https://t.me/{username}">@{username}</a>'


async def _add_watch(user_id: int, raw: str, lang: str) -> tuple[str, str | None]:
    """Username'ni kuzatuvga qo'shadi. Returns: (javob, username_or_None)."""
    result = await check_username(raw)

    if result.status == "invalid":
        return t(lang, "WATCH_INVALID", reason=t(lang, result.reason)), None
    if result.status == "free":
        return t(lang, "WATCH_FREE_NOW", username=result.username), None

    added = await storage.add_watch(user_id, result.username, "taken")
    if not added:
        return t(lang, "WATCH_ALREADY", username=result.username), result.username
    return t(lang, "WATCH_ADDED", username=result.username), result.username


@router.message(Command("watch"))
async def cmd_watch(message: Message, lang: str) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(t(lang, "USAGE_WATCH"))
        return
    await storage.upsert_user(message.from_user.id, message.from_user.username)
    text, username = await _add_watch(message.from_user.id, parts[1], lang)
    markup = None
    if username:
        markup = await ui.result_markup(username, lang, "taken", watching=True)
    await message.answer(text, reply_markup=markup)


@router.message(Command("unwatch"))
async def cmd_unwatch(message: Message, lang: str) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(t(lang, "USAGE_UNWATCH"))
        return
    username = validator.normalize(parts[1])
    removed = await storage.remove_watch(message.from_user.id, username)
    key = "UNWATCH_OK" if removed else "UNWATCH_NONE"
    await message.answer(t(lang, key, username=username))


@router.message(Command("autoclaim"))
async def cmd_autoclaim(message: Message, lang: str) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(t(lang, "USAGE_AUTOCLAIM"))
        return
    await storage.upsert_user(message.from_user.id, message.from_user.username)

    result = await check_username(parts[1])
    if result.status == "invalid":
        await message.answer(t(lang, "WATCH_INVALID", reason=t(lang, result.reason)))
        return
    if result.status == "free":
        # Allaqachon bo'sh — kutish shart emas.
        await message.answer(t(lang, "AUTOCLAIM_FREE_NOW", username=result.username))
        return

    outcome = await storage.add_auto_claim(message.from_user.id, result.username, "taken")
    key = "AUTOCLAIM_ALREADY" if outcome == "already" else "AUTOCLAIM_ADDED"
    await message.answer(t(lang, key, username=result.username))


@router.message(Command("list"))
async def cmd_list(message: Message, lang: str) -> None:
    rows = await storage.list_watch(message.from_user.id)
    if not rows:
        await message.answer(t(lang, "LIST_EMPTY"))
        return
    lines = [t(lang, "LIST_HEADER")]
    for r in rows:
        mark = "❌" if r["status"] == "taken" else "✅"
        robot = " 🤖" if r["auto_claim"] else ""
        lines.append(f"• {_link(r['target_username'])} — {mark}{robot}")
    await message.answer("\n".join(lines), link_preview_options=_NO_PREVIEW)


@router.message(Command("history"))
async def cmd_history(message: Message, lang: str) -> None:
    rows = await storage.recent_history(message.from_user.id, limit=10)
    if not rows:
        await message.answer(t(lang, "HISTORY_EMPTY"))
        return
    emoji = {"free": "✅", "taken": "❌", "unknown": "🤔", "invalid": "⚠️"}
    lines = [t(lang, "HISTORY_HEADER")]
    for r in rows:
        e = emoji.get(r["result"], "•")
        lines.append(f"{e} {_link(r['username'])} — {r['checked_at']}")
    await message.answer("\n".join(lines), link_preview_options=_NO_PREVIEW)


# --- Inline tugmalar ---

@router.callback_query(F.data.startswith("watch:"))
async def cb_watch(call: CallbackQuery, lang: str) -> None:
    username = call.data.split(":", 1)[1]
    await storage.upsert_user(call.from_user.id, call.from_user.username)
    added = await storage.add_watch(call.from_user.id, username, "taken")
    if added:
        await call.answer(t(lang, "CB_WATCH_ADDED"))
        await call.message.edit_reply_markup(
            reply_markup=await ui.result_markup(username, lang, "taken", watching=True)
        )
    else:
        await call.answer(t(lang, "CB_WATCH_ALREADY"))


@router.callback_query(F.data.startswith("unwatch:"))
async def cb_unwatch(call: CallbackQuery, lang: str) -> None:
    username = call.data.split(":", 1)[1]
    removed = await storage.remove_watch(call.from_user.id, username)
    if removed:
        await call.answer(t(lang, "CB_UNWATCH_OK"))
        await call.message.edit_reply_markup(
            reply_markup=await ui.result_markup(username, lang, "taken", watching=False)
        )
    else:
        await call.answer(t(lang, "CB_UNWATCH_NONE"))
