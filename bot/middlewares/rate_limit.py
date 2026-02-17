# bot/middlewares/rate_limit.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Rate limiting middleware.
    Prevents spam by limiting messages per user.
    """
    
    def __init__(self, rate_limit: int = 3, period: int = 1):
        """
        Args:
            rate_limit: Max messages per period
            period: Time period in seconds
        """
        self.rate_limit = rate_limit
        self.period = period
        self.user_messages: Dict[int, list] = {}
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        
        # Initialize user history
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        
        # Clean old messages
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if current_time - msg_time < self.period
        ]
        
        # Check rate limit
        if len(self.user_messages[user_id]) >= self.rate_limit:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            await event.answer(
                "⚠️ You're sending messages too fast. Please slow down."
            )
            return
        
        # Add current message
        self.user_messages[user_id].append(current_time)
        
        # Continue processing
        return await handler(event, data)