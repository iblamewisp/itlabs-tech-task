import logging
from apps.users.models import User

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def handle_bot_blocked(user: User) -> None:
        """
        Called when Telegram reports the user has blocked the bot.
        Deletes the user and all related data (tasks, categories cascade).
        """
        telegram_id = user.telegram_id
        user.delete()
        logger.warning(
            f"User {telegram_id} blocked the bot — deleted user and all their data"
        )
