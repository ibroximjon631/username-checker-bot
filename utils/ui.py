"""UI yordamchisi — natija klaviaturasini (Fragment ma'lumoti bilan) quradi.

check handler va watch/unwatch callbacklari shu yordamchidan foydalanadi —
takrorlanmasligi va izchillik uchun.
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

import keyboards
from config import settings
from services.fragment import check_fragment
from utils import cache


async def fragment_data(username: str) -> tuple[str | None, str | None]:
    """Username Fragment'da sotuvda bo'lsa (narx, url) qaytaradi. Aks holda (None, None)."""
    if not settings.fragment_enabled:
        return None, None
    raw = cache.get(f"frag:{username}")
    if raw is None:
        info = await check_fragment(username)
        raw = f"{info.state}|{info.status_text}|{info.price_ton}|{info.url}"
        cache.set(f"frag:{username}", raw, ttl=600)
    state, _status_text, price, url = raw.split("|", 3)
    if state == "for_sale" and price:
        return price, url
    return None, None


async def result_markup(
    username: str, lang: str, status: str, watching: bool = False
) -> InlineKeyboardMarkup | None:
    """Tekshiruv natijasi uchun to'liq klaviatura (Fragment tugmasi bilan)."""
    price, url = await fragment_data(username)
    return keyboards.result_keyboard(
        username, lang, status, watching=watching, frag_price=price, frag_url=url
    )
