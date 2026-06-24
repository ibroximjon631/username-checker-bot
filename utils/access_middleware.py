"""Access gate — tasdiqlanmagan foydalanuvchilarni bloklaydi.

Ruxsat etiladi:
  • adminlar (har doim)
  • tasdiqlangan (approved) foydalanuvchilar
  • /start buyrug'i (ro'yxatdan o'tish / holatni ko'rsatish uchun)
Qolganlar — "kuting/rad etildi" xabari bilan bloklanadi.

i18n middleware'dan KEYIN ulanishi kerak (lang allaqachon tayyor).
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User

from config import settings
from db import storage
from locales import t


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        # Adminlar — to'siqsiz
        if user.id in settings.admin_id_list:
            return await handler(event, data)

        status = await storage.get_status(user.id)
        if status == "approved":
            return await handler(event, data)

        # /start — ro'yxatdan o'tish uchun o'tkazamiz
        if isinstance(event, Message) and (event.text or "").startswith("/start"):
            return await handler(event, data)

        # Bloklaymiz
        lang = data.get("lang")
        key = "ACCESS_REJECTED" if status == "rejected" else "ACCESS_PENDING"
        if isinstance(event, Message):
            await event.answer(t(lang, key))
        elif isinstance(event, CallbackQuery):
            await event.answer(t(lang, key), show_alert=True)
        return None
