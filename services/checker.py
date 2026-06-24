"""Asosiy tekshiruv xizmati — validatsiya + t.me + (ixtiyoriy) Telethon.

Mantiq:
  1. Format validatsiya
  2. Kesh (agar use_cache=True)
  3. t.me parse (tez)
  4. Telethon yoqilgan bo'lsa — natijani tasdiqlaydi (aniqroq)
"""
from dataclasses import dataclass

from services import validator
from services import telethon_client
from services.tme_parser import check_tme
from utils import cache


@dataclass
class CheckResult:
    username: str
    status: str        # "free" | "taken" | "invalid" | "unknown"
    reason: str = ""   # invalid bo'lsa sabab
    source: str = ""   # "tme" | "telethon" | "cache"


async def check_username(raw: str, use_cache: bool = True) -> CheckResult:
    """Username'ni to'liq tekshiradi.

    use_cache=False — scheduler uchun (har doim yangi natija kerak).
    """
    username = validator.normalize(raw)

    ok, reason = validator.validate(username)
    if not ok:
        return CheckResult(username=username, status="invalid", reason=reason)

    # Keshdan qaraymiz
    if use_cache:
        cached = cache.get(username)
        if cached is not None:
            return CheckResult(username=username, status=cached, source="cache")

    # 1-qatlam: t.me
    status = await check_tme(username)
    source = "tme"

    # 2-qatlam: Telethon bilan tasdiqlash (yoqilgan bo'lsa)
    if telethon_client.is_enabled():
        tele = await telethon_client.check_telethon(username)
        if tele in ("free", "taken"):
            status = tele
            source = "telethon"

    # Aniq natijani keshlaymiz
    if status in ("free", "taken"):
        cache.set(username, status)

    return CheckResult(username=username, status=status, source=source)
