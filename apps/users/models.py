from django.db import models
from apps.core.fields import ULIDField
from apps.core.models import TimeStampedModel

class User(TimeStampedModel):
    id = ULIDField()
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username or self.telegram_id}"