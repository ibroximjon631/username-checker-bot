"""Inline klaviaturalar."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import LANG_NAMES, t


def result_keyboard(
    username: str,
    lang: str,
    status: str,
    watching: bool = False,
    frag_price: str | None = None,
    frag_url: str | None = None,
) -> InlineKeyboardMarkup | None:
    """Tekshiruv natijasi uchun tugmalar to'plami.

    • taken  → "Telegramda ochish" + "Kuzatish/Kuzatuvdan olish"
    • for_sale (frag) → "Fragment — N TON"
    • free/unknown → tugmasiz (faqat fragment bo'lsa)
    """
    kb = InlineKeyboardBuilder()
    has = False

    if status == "taken":
        kb.row(InlineKeyboardButton(
            text=t(lang, "BTN_OPEN"), url=f"https://t.me/{username}",
        ))
        has = True

    if frag_price and frag_url:
        kb.row(InlineKeyboardButton(
            text=f"💎 Fragment — {frag_price} TON", url=frag_url,
        ))
        has = True

    if status == "taken":
        if watching:
            kb.row(InlineKeyboardButton(
                text=t(lang, "BTN_UNWATCH"), callback_data=f"unwatch:{username}",
            ))
        else:
            kb.row(InlineKeyboardButton(
                text=t(lang, "BTN_WATCH"), callback_data=f"watch:{username}",
            ))
        has = True

    return kb.as_markup() if has else None


def lang_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, name in LANG_NAMES.items():
        kb.add(InlineKeyboardButton(text=name, callback_data=f"setlang:{code}"))
    kb.adjust(1)
    return kb.as_markup()


def approve_keyboard(user_id: int, lang: str) -> InlineKeyboardMarkup:
    """Admin uchun: tasdiqlash/rad etish tugmalari."""
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(
        text=t(lang, "BTN_APPROVE"), callback_data=f"approve:{user_id}",
    ))
    kb.add(InlineKeyboardButton(
        text=t(lang, "BTN_REJECT"), callback_data=f"reject:{user_id}",
    ))
    return kb.as_markup()
