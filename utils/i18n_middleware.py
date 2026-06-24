"""i18n middleware — har yangilanishda foydalanuvchi tilini aniqlaydi.

Tilni `data["lang"]` ga qo'yadi, handlerlar uni qabul qiladi.
Tezlik uchun til xotirada keshlanadi.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from db import storage
from locales import DEFAULT_LANG, TEXTS

# Xotiradagi til keshi: user_id -> lang
_lang_cache: dict[int, str] = {}


def invalidate(user_id: int) -> None:
    """Til o'zgartirilganda keshni yangilash uchun."""
    _lang_cache.pop(user_id, None)


def _guess_from_telegram(user: User) -> str:
    """Telegram tilidan taxmin qiladi (faqat birinchi kirishda)."""
    code = (user.language_code or "")[:2].lower()
    return code if code in TEXTS else DEFAULT_LANG


class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        lang = DEFAULT_LANG

        if user is not None:
            cached = _lang_cache.get(user.id)
            if cached is not None:
                lang = cached
            else:
                stored = await storage.get_lang(user.id)
                lang = stored or _guess_from_telegram(user)
                _lang_cache[user.id] = lang

        data["lang"] = lang
        return await handler(event, data)
