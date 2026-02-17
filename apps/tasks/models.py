from django.db import models
from apps.core.models import TimeStampedModel
from apps.core.fields import ULIDField
from apps.users.models import User


class Category(TimeStampedModel):
    """Task category model"""
    id = ULIDField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return self.name


class Task(TimeStampedModel):
    """Task model with smart reminders"""
    id = ULIDField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    is_completed = models.BooleanField(default=False)
    
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Task deadline (user sets this)"
    )
    
    next_reminder_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Next calculated reminder time (auto-calculated)"
    )
    
    last_reminder_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was the last reminder sent"
    )
    
    reminder_level = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily (5+ days left)'),
            ('half_day', 'Half-day (2-5 days left)'),
            ('quarter_day', 'Quarter-day (1-2 days left)'),
            ('urgent', 'Urgent (< 1 day left)'),
            ('final', 'Final (< 2 hours left)'),
            ('overdue', 'Overdue'),
        ],
        default='daily',
        help_text="Current reminder intensity level"
    )
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['user', 'is_completed']),
            models.Index(fields=['next_reminder_time']),  # for efficient celery requests, i placed idx on next_time
            models.Index(fields=['deadline']),
        ]
    
    def __str__(self):
        return self.title