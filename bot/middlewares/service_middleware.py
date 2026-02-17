from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.backend.factory import create_backend
from bot.services import TaskService, UserService


class ServiceMiddleware(BaseMiddleware):
    """Inject TaskService into handler context"""
    
    def __init__(self):
        backend = create_backend()
        self.task_service = TaskService(backend)
        self.user_service = UserService(backend)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['task_service'] = self.task_service
        data['user_service'] = self.user_service
        return await handler(event, data)