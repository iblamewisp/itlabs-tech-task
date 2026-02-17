# apps/tasks/notifications/telegram.py
from aiogram import Bot
from django.conf import settings
import asyncio
import logging
from typing import Optional
from .base import NotificationChannel

logger = logging.getLogger(__name__)


class TelegramNotification(NotificationChannel):
    """Telegram notification implementation"""
    
    # Instance variables (per-worker)
    _bot: Optional[Bot] = None
    _loop: Optional[asyncio.AbstractEventLoop] = None
    
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or settings.BOT_TOKEN
        self._ensure_bot()
    
    def _ensure_bot(self) -> None:
        """Ensure bot instance exists in this worker"""
        if TelegramNotification._bot is None:
            TelegramNotification._bot = Bot(token=self.bot_token)
            logger.info("Created Bot instance in Celery worker")
    
    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop"""
        if TelegramNotification._loop is None or TelegramNotification._loop.is_closed():
            try:
                TelegramNotification._loop = asyncio.get_event_loop()
            except RuntimeError:
                TelegramNotification._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(TelegramNotification._loop)
        
        return TelegramNotification._loop
    
    def send(self, recipient_id: int, message: str) -> bool:
        """Send Telegram message"""
        try:
            loop = self._get_event_loop()
            
            # Use shared bot
            loop.run_until_complete(
                TelegramNotification._bot.send_message(
                    chat_id=recipient_id,
                    text=message
                )
            )
            
            logger.info(f"Notification sent to {recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send to {recipient_id}: {e}")
            return False
    
    @classmethod
    def cleanup(cls) -> None:
        """Cleanup bot session (call on worker shutdown)"""
        if cls._bot:
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(cls._bot.session.close())
                logger.info("Closed Bot session")
            except Exception as e:
                logger.error(f"Error closing bot session: {e}")
            finally:
                cls._bot = None