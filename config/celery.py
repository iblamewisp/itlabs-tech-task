from celery import Celery
from celery.signals import worker_process_shutdown
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('todo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@worker_process_shutdown.connect
def cleanup_worker(**kwargs):
    """Cleanup resources when worker shuts down"""
    from apps.tasks.notifications.telegram import TelegramNotification
    
    TelegramNotification.cleanup()