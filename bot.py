"""Telegram Username Checker Bot — kirish nuqtasi."""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from loguru import logger

from config import settings
from db import storage
from handlers import start, check, monitor, generate, admin, access, errors
from scheduler import setup_scheduler
from services import telethon_client
from utils.access_middleware import AccessMiddleware
from utils.i18n_middleware import I18nMiddleware
from utils.logger import setup_logger


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="check", description="Username tekshirish"),
        BotCommand(command="gen", description="Bo'sh username topish"),
        BotCommand(command="watch", description="Kuzatuvga qo'shish"),
        BotCommand(command="unwatch", description="Kuzatuvdan olish"),
        BotCommand(command="list", description="Kuzatuv ro'yxati"),
        BotCommand(command="history", description="Tekshiruvlar tarixi"),
        BotCommand(command="lang", description="Til / Язык / Language"),
        BotCommand(command="help", description="Yordam"),
    ])


async def main() -> None:
    setup_logger()
    logger.info("Bot ishga tushmoqda…")

    # Tashqi xizmatlar
    await storage.init_db()
    await telethon_client.init_telethon()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Middleware tartibi muhim: avval til (i18n), keyin kirish nazorati (access)
    dp.message.middleware(I18nMiddleware())
    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
    dp.callback_query.middleware(AccessMiddleware())

    # Handlerlar (check oxirida — u oddiy matnni ushlaydi)
    dp.include_router(errors.router)
    dp.include_router(start.router)
    dp.include_router(access.router)
    dp.include_router(admin.router)
    dp.include_router(monitor.router)
    dp.include_router(generate.router)
    dp.include_router(check.router)

    await set_commands(bot)
    scheduler = setup_scheduler(bot)

    me = await bot.get_me()
    logger.info(f"Bot tayyor: @{me.username}")

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await telethon_client.close_telethon()
        await storage.close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
