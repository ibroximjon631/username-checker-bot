"""/start, /help, /lang va kirish so'rovi (access request)."""
from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message
from loguru import logger

import keyboards
from config import settings
from db import storage
from locales import DEFAULT_LANG, t
from utils import i18n_middleware

router = Router(name="start")


async def _notify_admins(bot: Bot, user) -> None:
    """Yangi so'rov haqida barcha adminlarga xabar yuboradi."""
    name = user.full_name
    username = f"@{user.username}" if user.username else "—"
    for admin_id in settings.admin_id_list:
        alang = await storage.get_lang(admin_id) or DEFAULT_LANG
        try:
            await bot.send_message(
                admin_id,
                t(alang, "ADMIN_NEW_REQUEST", name=name, username=username, uid=user.id),
                reply_markup=keyboards.approve_keyboard(user.id, alang),
            )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Adminga ({admin_id}) so'rov yuborilmadi: {e}")


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str, bot: Bot) -> None:
    user = message.from_user
    name = user.first_name if user else "friend"

    prev_status = await storage.get_status(user.id)
    await storage.upsert_user(user.id, user.username)

    # Adminlar — har doim tasdiqlangan
    if user.id in settings.admin_id_list:
        if prev_status != "approved":
            await storage.set_status(user.id, "approved")
        await message.answer(t(lang, "START", name=name))
        return

    if prev_status is None:
        # Yangi foydalanuvchi — so'rov yuboramiz (yangi yozuv default 'pending')
        await message.answer(t(lang, "ACCESS_REQUESTED"))
        await _notify_admins(bot, user)
        logger.info(f"Yangi ruxsat so'rovi: {user.id} (@{user.username})")
    elif prev_status == "approved":
        await message.answer(t(lang, "START", name=name))
    elif prev_status == "rejected":
        await message.answer(t(lang, "ACCESS_REJECTED"))
    else:  # pending
        await message.answer(t(lang, "ACCESS_PENDING"))


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str) -> None:
    await message.answer(t(lang, "HELP"))


@router.message(Command("lang"))
async def cmd_lang(message: Message, lang: str) -> None:
    await message.answer(t(lang, "LANG_CHOOSE"), reply_markup=keyboards.lang_keyboard())


@router.callback_query(F.data.startswith("setlang:"))
async def cb_setlang(call: CallbackQuery) -> None:
    new_lang = call.data.split(":", 1)[1]
    await storage.upsert_user(call.from_user.id, call.from_user.username)
    await storage.set_lang(call.from_user.id, new_lang)
    i18n_middleware.invalidate(call.from_user.id)
    await call.answer()
    await call.message.edit_text(t(new_lang, "LANG_SET"))
