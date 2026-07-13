"""
Throttling middleware — limits user request rate.
"""
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple in-memory rate limiter.
    rate: minimum seconds between messages per user.
    """

    def __init__(self, rate: float = 0.5):
        self.rate = rate
        self.cache: TTLCache = TTLCache(maxsize=10_000, ttl=rate)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            if user.id in self.cache:
                return  # throttled — silently drop
            self.cache[user.id] = True

        return await handler(event, data)
