from typing import Optional
from datetime import datetime
from django.db import transaction
from apps.tasks.models import Task
from apps.tasks.services.reminder_calculator import ReminderCalculator
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for managing task reminders (Single Responsibility)"""
    
    @staticmethod
    def set_initial_reminder(task: Task) -> None:
        """
        Set initial reminder for a new task with deadline

        Args:
            task: Task instance with deadline set
        """
        from django.utils import timezone

        if not task.deadline:
            logger.warning(f"Task {task.id} has no deadline, skipping reminder setup")
            return

        logger.info(f"=== Setting up reminder for task {task.id} ===")
        logger.info(f"  Deadline: {task.deadline} (type: {type(task.deadline).__name__})")
        logger.info(f"  Deadline timezone: {task.deadline.tzinfo}")
        logger.info(f"  Current time: {timezone.now()}")
        logger.info(f"  Current timezone: {timezone.now().tzinfo}")

        next_reminder, level = ReminderCalculator.calculate_next_reminder(
            deadline=task.deadline
        )

        task.next_reminder_time = next_reminder
        task.reminder_level = level
        task.save(update_fields=['next_reminder_time', 'reminder_level'])

        time_until = next_reminder - timezone.now()
        logger.info(
            f"✓ Initial reminder set for task {task.id}: "
            f"{next_reminder} (level: {level})"
        )
        logger.info(f"  Time until reminder: {time_until}")
        logger.info(f"=== Reminder setup complete ===")
    
    @staticmethod
    def update_reminder_after_deadline_change(
        task: Task,
        new_deadline: Optional[datetime]
    ) -> None:
        """
        Recalculate reminder after deadline change
        
        Args:
            task: Task instance
            new_deadline: New deadline (None to clear reminders)
        """
        task.deadline = new_deadline
        
        if new_deadline:
            next_reminder, level = ReminderCalculator.calculate_next_reminder(
                deadline=new_deadline,
                last_reminder=task.last_reminder_sent
            )
            task.next_reminder_time = next_reminder
            task.reminder_level = level
        else:
            # Clear reminders
            task.next_reminder_time = None
            task.reminder_level = 'daily'
            task.last_reminder_sent = None
        
        task.save(update_fields=['deadline', 'next_reminder_time', 'reminder_level', 'last_reminder_sent'])

        logger.info(f"Reminder updated for task {task.id} with new deadline {new_deadline}")
    
    @staticmethod
    @transaction.atomic
    def mark_reminder_sent_and_schedule_next(task: Task) -> None:
        """
        Mark reminder as sent and schedule next one
        
        Args:
            task: Task instance
        """
        from django.utils import timezone
        
        # Calculate next reminder before updating last_reminder_sent
        previous_reminder_sent = task.last_reminder_sent
        next_reminder, new_level = ReminderCalculator.calculate_next_reminder(
            deadline=task.deadline,
            last_reminder=previous_reminder_sent
        )

        # Update last reminder time
        task.last_reminder_sent = timezone.now()
        
        task.next_reminder_time = next_reminder
        task.reminder_level = new_level
        
        task.save(update_fields=['last_reminder_sent', 'next_reminder_time', 'reminder_level'])
        
        logger.info(
            f"Reminder marked as sent for task {task.id}. "
            f"Next: {next_reminder} (level: {new_level})"
        )