from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.utils import timezone
from apps.tasks.services.task_service import TaskService
from apps.tasks.services.notification_service import NotificationService
from apps.tasks.services.reminder_service import ReminderService
from apps.tasks.notifications.telegram import TelegramNotification
from apps.tasks.models import Task
import logging

logger = logging.getLogger(__name__)


@shared_task(time_limit=30)
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


@shared_task(
    bind=True,
    max_retries=3,
    time_limit=30,
    soft_time_limit=25,
)
def send_smart_reminder(self, task_id: str):
    """
    Send smart reminder for a single task.

    Retries up to 3 times with exponential backoff (60s → 120s → 240s).
    Responsibility: ONLY coordination (delegates to services)
    """
    try:
        task = Task.objects.select_related('user', 'category').get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {'success': False, 'error': 'Task not found'}

    try:
        notification_service = NotificationService(TelegramNotification())
        success = notification_service.send_reminder(task)
    except SoftTimeLimitExceeded:
        logger.warning(f"Notification timed out for task {task_id}, retrying")
        raise self.retry(countdown=60 * (2 ** self.request.retries))

    if not success:
        logger.warning(
            f"Notification failed for task {task_id} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1})"
        )
        raise self.retry(countdown=60 * (2 ** self.request.retries))

    ReminderService.mark_reminder_sent_and_schedule_next(task)

    return {
        'success': True,
        'task_id': task_id,
        'reminder_level': task.reminder_level,
        'next_reminder': task.next_reminder_time.isoformat() if task.next_reminder_time else None
    }