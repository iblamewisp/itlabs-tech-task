from celery import shared_task
from django.utils import timezone
from apps.tasks.services.task_service import TaskService
from apps.tasks.services.notification_service import NotificationService
from apps.tasks.services.reminder_service import ReminderService
from apps.tasks.notifications.telegram import TelegramNotification
from apps.tasks.models import Task
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_smart_reminders():
    """
    Check for tasks needing smart reminders.
    Runs every minute via Celery Beat.
    
    Responsibility: ONLY scheduling (coordination)
    """
    # Delegate query to TaskService — evaluate once to avoid double DB hit
    tasks_to_remind = list(TaskService.get_tasks_needing_reminders())

    logger.info(f"Found {len(tasks_to_remind)} tasks needing reminders")

    # Schedule individual reminder tasks
    for task in tasks_to_remind:
        send_smart_reminder.delay(str(task.id))

    return {
        'checked_at': timezone.now().isoformat(),
        'tasks_found': len(tasks_to_remind)
    }


@shared_task
def send_smart_reminder(task_id: str):
    """
    Send smart reminder for a single task
    
    Responsibility: ONLY coordination (delegates to services)
    """
    try:
        task = Task.objects.select_related('user', 'category').get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {'success': False, 'error': 'Task not found'}
    
    # Delegate notification to NotificationService
    notification_service = NotificationService(TelegramNotification())
    success = notification_service.send_reminder(task)
    
    if success:
        # Delegate reminder update to ReminderService
        ReminderService.mark_reminder_sent_and_schedule_next(task)
    
    return {
        'success': success,
        'task_id': task_id,
        'reminder_level': task.reminder_level,
        'next_reminder': task.next_reminder_time.isoformat() if task.next_reminder_time else None
    }