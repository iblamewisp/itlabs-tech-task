from typing import Optional
from django.db import transaction
from apps.tasks.models import Task, Category
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task business logic (Django-side)"""
    
    @staticmethod
    @transaction.atomic
    def create_task(
        user: User,
        title: str,
        description: str = '',
        category: Optional[Category] = None,
        deadline: Optional[str] = None
    ) -> Task:
        """Create new task"""
        task = Task.objects.create(
            user=user,
            title=title,
            description=description,
            category=category,
            deadline=deadline
        )

        # Set up smart reminders if deadline is provided
        if deadline:
            from apps.tasks.services.reminder_service import ReminderService
            ReminderService.set_initial_reminder(task)

        logger.info(f"Task created: {task.id} for user {user.telegram_id}")
        return task
    
    @staticmethod
    @transaction.atomic
    def complete_task(task: Task) -> Task:
        """Mark task as completed"""
        task.is_completed = True
        task.save(update_fields=['is_completed', 'updated_at'])
        
        logger.info(f"Task completed: {task.id}")
        return task
    
    @staticmethod
    @transaction.atomic
    def uncomplete_task(task: Task) -> Task:
        """Mark task as not completed"""
        task.is_completed = False
        task.save(update_fields=['is_completed', 'updated_at'])
        
        logger.info(f"Task uncompleted: {task.id}")
        return task
    
    @staticmethod
    @transaction.atomic
    def update_task(
        task: Task,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[Category] = None,
        deadline: Optional[str] = None,
    ) -> Task:
        """Update task"""
        deadline_changed = False

        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if category is not None:
            task.category = category

        if deadline is not None:
            old_deadline = task.deadline
            if old_deadline != deadline:
                deadline_changed = True
                # Don't save here - ReminderService will handle it
            else:
                task.deadline = deadline

        if not deadline_changed:
            update_fields = ['updated_at']
            if title is not None:
                update_fields.append('title')
            if description is not None:
                update_fields.append('description')
            if category is not None:
                update_fields.append('category')
            task.save(update_fields=update_fields)

        # Update reminders if deadline changed
        if deadline_changed:
            from apps.tasks.services.reminder_service import ReminderService
            ReminderService.update_reminder_after_deadline_change(task, deadline)

        logger.info(f"Task updated: {task.id}")
        return task
    
    @staticmethod
    @transaction.atomic
    def delete_task(task: Task) -> None:
        """Delete task"""
        task_id = task.id
        task.delete()
        logger.info(f"Task deleted: {task_id}")

    @staticmethod
    def get_tasks_needing_reminders():
        """
        Get tasks that need reminders sent now

        Returns:
            QuerySet: Tasks where next_reminder_time has passed
        """
        from django.utils import timezone

        return Task.objects.filter(
            is_completed=False,
            deadline__isnull=False,
            next_reminder_time__isnull=False,
            next_reminder_time__lte=timezone.now()
        ).select_related('user', 'category')