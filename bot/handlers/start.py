from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.services.user_service import UserService
from bot.keyboards.main_menu import get_main_menu_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user_service: UserService):
    """Handle /start command"""
    user = message.from_user
    
    try:
        user_dto = await user_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username or '',
            first_name=user.first_name or ''
        )
        
        await message.answer(
            f"👋 Hello, {user_dto.first_name}!\n\n"
            "I'm your TODO bot. I can help you:\n"
            "• Create tasks\n"
            "• Set reminders\n"
            "• Organize with categories\n"
            "• Track your progress\n\n"
            "Use the menu below to get started!",
            reply_markup=get_main_menu_keyboard()
        )
        
        logger.info(f"User {user.id} started the bot")
        
    except Exception as e:
        logger.error(f"Failed to register user {user.id}: {e}")
        await message.answer("❌ Failed to start. Please try again later.")