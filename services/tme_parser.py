"""t.me sahifasini o'qib username band/bo'shligini aniqlaydi.

Bot API username availability'ni bermaydi, shuning uchun ochiq
https://t.me/<username> sahifasini tahlil qilamiz.
"""
import aiohttp
from loguru import logger

TME_URL = "https://t.me/{username}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

# t.me sahifasidagi belgilovchi iboralar.
# Band username sahifasida quyidagilar bo'ladi:
TAKEN_MARKERS = (
    "tgme_page_title",      # profil sarlavhasi bloki
    "tgme_page_extra",      # qo'shimcha ma'lumot (a'zolar soni h.k.)
)

# Yaroqli t.me sahifasida (band ham, bo'sh ham) doim shu blok bo'ladi.
# Rate-limit / xato / to'liqsiz javobda bu BO'LMAYDI — o'shanda "free" emas,
# "unknown" qaytaramiz (aks holda band username soxta "bo'sh" bo'lib ketadi).
VALID_PAGE_MARKER = "tgme_page_wrap"


async def check_tme(username: str) -> str:
    """Username holatini t.me orqali aniqlaydi.

    Returns:
        "taken"  — band
        "free"   — ehtimol bo'sh
        "unknown" — aniqlab bo'lmadi (tarmoq/xato)
    """
    url = TME_URL.format(username=username)
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"t.me {username}: status {resp.status}")
                    return "unknown"
                html = await resp.text()
    except Exception as e:  # noqa: BLE001
        logger.error(f"t.me so'rov xatosi ({username}): {e}")
        return "unknown"

    # Profil bloki bor — aniq band.
    if any(marker in html for marker in TAKEN_MARKERS):
        return "taken"

    # Profil bloki yo'q. Lekin bu haqiqatan bo'sh sahifami yoki buzuq javobmi?
    # Yaroqli t.me sahifasi belgisi bo'lsagina "bo'sh" deymiz; aks holda "unknown".
    if VALID_PAGE_MARKER in html:
        return "free"

    logger.warning(
        f"t.me {username}: profil bloki ham, sahifa belgisi ham yo'q "
        f"(ehtimol rate-limit/buzuq javob) — 'unknown' qaytarildi"
    )
    return "unknown"
