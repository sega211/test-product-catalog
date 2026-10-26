import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.config import load_settings
from app.handlers import router


async def main() -> None:
    settings = load_settings()

    logging.basicConfig(level=logging.INFO)

    if settings.telegram_proxy:
        session = AiohttpSession(proxy=settings.telegram_proxy)
        bot = Bot(token=settings.bot_token, session=session)
        logging.info("Telegram API proxy is enabled")
    else:
        bot = Bot(token=settings.bot_token)
        logging.info("Telegram API proxy is disabled")
    dispatcher = Dispatcher()

    dispatcher["settings"] = settings
    dispatcher.include_router(router)

    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
