"""Username generator — pattern yoki so'zlar ro'yxatidan bo'sh username topadi.

Qo'llab-quvvatlanadigan formatlar:
  • Wildcard:  gold*    →  gold + 1 belgi (gold0..goldz)
                go*d     →  o'rtada wildcard ham bo'ladi
                co**      →  ikkita wildcard (a-z0-9)
  • Ro'yxat:   alpha beta gamma   →  har birini tekshiradi
"""
from __future__ import annotations

import asyncio
import itertools
from dataclasses import dataclass

from services import validator
from services.checker import check_username

WILDCARD_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"  # 36 belgi
MAX_CANDIDATES = 40      # flood himoyasi — ko'pi bilan shuncha tekshiriladi
CONCURRENCY = 5          # bir vaqtda nechta so'rov


@dataclass
class GenResult:
    free: list[str]
    checked: int
    truncated: bool      # ko'p bo'lib qisqartirildimi
    error: str = ""


def _expand(pattern: str) -> tuple[list[str], bool]:
    """Wildcardli patternni nomzodlarga yoyadi.

    Returns: (nomzodlar, truncated)
    """
    star_count = pattern.count("*")
    # Har bir wildcard 36 variant — portlashdan saqlanamiz
    total = len(WILDCARD_ALPHABET) ** star_count
    truncated = total > MAX_CANDIDATES

    slots = [WILDCARD_ALPHABET if ch == "*" else ch for ch in pattern]
    candidates: list[str] = []
    for combo in itertools.product(*slots):
        candidates.append("".join(combo))
        if len(candidates) >= MAX_CANDIDATES:
            break
    return candidates, truncated


def _parse_input(text: str) -> tuple[list[str], bool]:
    """Foydalanuvchi kiritmasini nomzodlar ro'yxatiga aylantiradi."""
    text = text.strip().lower()
    if "*" in text:
        # Faqat birinchi so'zni (patternni) olamiz
        pattern = text.split()[0]
        return _expand(pattern)
    # Bo'sh joy bilan ajratilgan so'zlar ro'yxati
    words = [validator.normalize(w) for w in text.split()]
    return words[:MAX_CANDIDATES], len(words) > MAX_CANDIDATES


async def generate(text: str) -> GenResult:
    candidates, truncated = _parse_input(text)

    # Faqat formatga to'g'ri keladiganlarni qoldiramiz
    valid = [c for c in candidates if validator.validate(c)[0]]
    if not valid:
        return GenResult(
            free=[], checked=0, truncated=truncated,
            error="To'g'ri nomzod topilmadi. Misol: <code>/gen gold*</code>",
        )

    sem = asyncio.Semaphore(CONCURRENCY)

    async def _one(name: str) -> tuple[str, str]:
        async with sem:
            res = await check_username(name)
            return name, res.status

    pairs = await asyncio.gather(*[_one(c) for c in valid])
    free = [name for name, status in pairs if status == "free"]
    return GenResult(free=free, checked=len(valid), truncated=truncated)
