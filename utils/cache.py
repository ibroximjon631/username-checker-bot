"""Oddiy TTL (vaqt cheklangan) kesh.

Yaqinda tekshirilgan username'larni saqlaydi — takror so'rov tezroq
bo'ladi va Telegram'ga ortiqcha murojaat kamayadi (flood himoyasi).
"""
import time

_store: dict[str, tuple[str, float]] = {}
DEFAULT_TTL = 300.0  # 5 daqiqa


def get(key: str) -> str | None:
    """Keshdan qiymat oladi. Eskirgan/yo'q bo'lsa None."""
    item = _store.get(key)
    if item is None:
        return None
    value, expires = item
    if time.time() > expires:
        _store.pop(key, None)
        return None
    return value


def set(key: str, value: str, ttl: float = DEFAULT_TTL) -> None:
    _store[key] = (value, time.time() + ttl)


def clear() -> None:
    _store.clear()
