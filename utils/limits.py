"""Kunlik tekshiruv limiti.

Adminlar uchun cheksiz. Boshqalar uchun .env'dagi FREE_DAILY_LIMIT.
"""
from config import settings
from db import storage


async def allow(user_id: int) -> bool:
    """Foydalanuvchi yana tekshira oladimi? Ruxsat bo'lsa hisobni oshiradi."""
    if user_id in settings.admin_id_list:
        return True
    count = await storage.get_usage_today(user_id)
    if count >= settings.free_daily_limit:
        return False
    await storage.bump_usage_today(user_id)
    return True
