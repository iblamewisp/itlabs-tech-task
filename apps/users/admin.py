from django.contrib import admin
from django.db.models import Count
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'telegram_id', 'task_count', 'created_at')
    search_fields = ('username', 'first_name', 'telegram_id')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_task_count=Count('tasks'))

    def task_count(self, obj):
        return obj._task_count
    task_count.short_description = 'Tasks'
    task_count.admin_order_field = '_task_count'
