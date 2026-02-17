from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'telegram_id', 'task_count', 'created_at')
    search_fields = ('username', 'first_name', 'telegram_id')
    readonly_fields = ('created_at', 'updated_at')

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'
