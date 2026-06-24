"""Generator handleri: /gen — bo'sh username topadi."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from locales import t
from services.generator import generate
from utils import limits

router = Router(name="generate")


@router.message(Command("gen"))
async def cmd_gen(message: Message, lang: str) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(t(lang, "GEN_USAGE"))
        return

    if message.from_user and not await limits.allow(message.from_user.id):
        await message.answer(t(lang, "LIMIT_REACHED", limit=settings.free_daily_limit))
        return

    query = parts[1].strip()
    wait = await message.answer(t(lang, "GEN_SEARCHING", q=query))
    result = await generate(query)

    if result.error:
        await wait.edit_text(t(lang, "GEN_NO_VALID"))
        return
    if not result.free:
        await wait.edit_text(t(lang, "GEN_NONE", checked=result.checked))
        return

    names = "\n".join(f"✅ <code>@{n}</code>" for n in result.free)
    text = t(lang, "GEN_FOUND", count=len(result.free), checked=result.checked, names=names)
    if result.truncated:
        text += t(lang, "GEN_TRUNCATED")
    await wait.edit_text(text)
