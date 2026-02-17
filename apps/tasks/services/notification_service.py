from apps.tasks.notifications.base import NotificationChannel
from apps.tasks.models import Task
from apps.tasks.formatters.reminder_formatter import ReminderFormatter
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self, channel: NotificationChannel):
        self.channel = channel
    
    def send_reminder(self, task: Task) -> bool:
        """
        Send reminder for a task
        
        Args:
            task: Task instance
            
        Returns:
            bool: True if sent successfully
        """
        
        message = ReminderFormatter.format_reminder_message(task)
        
        # Send via channel
        success = self.channel.send(
            recipient_id=task.user.telegram_id,
            message=message
        )
        
        if success:
            logger.info(f"Reminder sent for task {task.id}")
        else:
            logger.error(f"Failed to send reminder for task {task.id}")
        
        return success