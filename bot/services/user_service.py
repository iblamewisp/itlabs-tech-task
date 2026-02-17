from bot.backend.base import IBackendAPI
from bot.dto import UserDTO
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations (bot-side)"""
    
    def __init__(self, backend: IBackendAPI):
        self.backend = backend
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str = '',
        first_name: str = ''
    ) -> UserDTO:
        """
        Get or create user
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            
        Returns:
            UserDTO: User data
        """
        return await self.backend.get_or_create_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )