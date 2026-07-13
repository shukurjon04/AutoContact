"""
Aiogram 3.x Bot entry point.
Uses webhook mode in production, polling in development.
"""
import asyncio
import logging
import os
import sys

import django
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Django setup must come before any app imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()

from django.conf import settings
from bot.handlers import register_all_routers
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.throttle import ThrottlingMiddleware

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    webhook_url = f"{settings.WEBHOOK_HOST}{settings.WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.WEBHOOK_SECRET_TOKEN,
        drop_pending_updates=True,
    )
    logger.info("Webhook set to: %s", webhook_url)


async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot shutting down, deleting webhook...")
    await bot.delete_webhook()


def create_bot() -> Bot:
    return Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)

    # Middlewares
    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate=0.5))

    # Routers
    register_all_routers(dp)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    return dp


def run_webhook():
    """Production: webhook mode via aiohttp."""
    bot = create_bot()
    dp = create_dispatcher()

    app = web.Application()
    handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET_TOKEN,
    )
    handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=8080)


def run_polling():
    """Development: polling mode."""
    bot = create_bot()
    dp = create_dispatcher()

    async def start():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    asyncio.run(start())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    mode = os.getenv("BOT_MODE", "webhook")
    if mode == "polling":
        logger.info("Starting bot in POLLING mode")
        run_polling()
    else:
        logger.info("Starting bot in WEBHOOK mode")
        run_webhook()
