"""Telegram username format validatsiyasi."""
import re

# Telegram qoidalari:
#  - 5–32 belgi
#  - faqat a-z, 0-9, _
#  - harf bilan boshlanadi
#  - raqam yoki _ bilan boshlanmaydi/tugamaydi
#  - ketma-ket ikkita _ bo'lmaydi
USERNAME_RE = re.compile(r"^[a-z][a-z0-9_]{3,30}[a-z0-9]$")


def normalize(username: str) -> str:
    """@ va bo'shliqlarni olib tashlab, kichik harfga keltiradi.

    t.me/foo yoki https://t.me/foo ko'rinishini ham qabul qiladi.
    """
    username = username.strip()
    username = re.sub(r"^https?://", "", username, flags=re.IGNORECASE)
    username = re.sub(r"^(t\.me/|telegram\.me/)", "", username, flags=re.IGNORECASE)
    username = username.lstrip("@").strip().lower()
    return username


def validate(username: str) -> tuple[bool, str]:
    """Username formatini tekshiradi.

    Returns:
        (ok, reason_key) — ok=True bo'lsa reason_key bo'sh.
        reason_key — locales'dagi xato kaliti (ERR_*), tarjima handlerda bo'ladi.
    """
    if not username:
        return False, "ERR_EMPTY"
    if len(username) < 5:
        return False, "ERR_SHORT"
    if len(username) > 32:
        return False, "ERR_LONG"
    if "__" in username:
        return False, "ERR_DOUBLE"
    if not USERNAME_RE.match(username):
        return False, "ERR_FORMAT"
    return True, ""
