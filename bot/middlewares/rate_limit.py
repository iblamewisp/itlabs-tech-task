# bot/middlewares/rate_limit.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Rate limiting middleware for both messages and callback queries.
    Prevents spam by limiting events per user.
    """

    def __init__(self, rate_limit: int = 3, period: int = 1):
        """
        Args:
            rate_limit: Max events per period
            period: Time period in seconds
        """
        self.rate_limit = rate_limit
        self.period = period
        self.user_events: Dict[int, list] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        from_user = getattr(event, 'from_user', None)
        if not from_user:
            return await handler(event, data)

        user_id = from_user.id
        current_time = time.time()

        if user_id not in self.user_events:
            self.user_events[user_id] = []

        # Drop timestamps outside the window
        self.user_events[user_id] = [
            t for t in self.user_events[user_id]
            if current_time - t < self.period
        ]

        if len(self.user_events[user_id]) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            if isinstance(event, Message):
                await event.answer("⚠️ You're sending messages too fast. Please slow down.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Too fast! Slow down.", show_alert=False)
            return

        self.user_events[user_id].append(current_time)
        return await handler(event, data)