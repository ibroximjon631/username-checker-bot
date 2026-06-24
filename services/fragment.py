"""Fragment.com integratsiyasi — username sotuvda/auksionda ekanini aniqlaydi.

Fragment'da rasmiy API yo'q, shuning uchun /username/<name> sahifasi tahlil
qilinadi (best-effort). Sahifa tuzilishi o'zgarsa, yangilanishi kerak.

Holatlar:
  for_sale — sotuvda / auksionda (narx bor)
  taken    — band (egasi bor, sotuvda emas)
  sold     — sotilgan
  unlisted — Fragment'da alohida e'lon emas (qidiruvga yo'naltirildi)
  unknown  — tarmoq/xato
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import aiohttp
from loguru import logger

URL = "https://fragment.com/username/{username}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

_STATUS_RE = re.compile(
    r'tm-section-header-status (tm-status-\w+)"[^>]*>([^<]+)<'
)
_PRICE_RE = re.compile(r'tm-value icon-before icon-ton[^>]*>([\d ,]+)')

_CLASS_MAP = {
    "tm-status-avail": "for_sale",
    "tm-status-taken": "taken",
    "tm-status-unavail": "sold",
}


@dataclass
class FragmentInfo:
    state: str               # for_sale | taken | sold | unlisted | unknown
    status_text: str = ""    # Fragment ko'rsatgan matn (masalan "On auction")
    price_ton: str = ""      # TON narxi (faqat for_sale)
    url: str = ""


async def check_fragment(username: str) -> FragmentInfo:
    url = URL.format(username=username)
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return FragmentInfo(state="unknown", url=url)
                html = await resp.text()
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Fragment so'rov xatosi ({username}): {e}")
        return FragmentInfo(state="unknown", url=url)

    m = _STATUS_RE.search(html)
    if not m:
        # Alohida e'lon emas (qidiruv sahifasiga yo'naltirilgan)
        return FragmentInfo(state="unlisted", url=url)

    state = _CLASS_MAP.get(m.group(1), "unknown")
    status_text = m.group(2).strip()

    price = ""
    if state == "for_sale":
        pm = _PRICE_RE.search(html)
        if pm:
            price = pm.group(1).strip()

    return FragmentInfo(state=state, status_text=status_text, price_ton=price, url=url)
