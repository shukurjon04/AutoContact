"""
Middleware: ensures Django ORM is available (Django setup already done in main.py).
Sets user object on data dict for handlers.
"""
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    """Injects TelegramUser into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from asgiref.sync import sync_to_async
        from apps.users.models import TelegramUser

        tg_user = data.get("event_from_user")
        if tg_user:
            try:
                user = await sync_to_async(
                    TelegramUser.objects.filter(telegram_id=tg_user.id).first
                )()
                data["db_user"] = user
            except Exception:
                logger.exception("DbSessionMiddleware: failed to fetch user")
                data["db_user"] = None

        return await handler(event, data)
