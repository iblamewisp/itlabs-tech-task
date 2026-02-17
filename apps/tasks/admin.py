from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'task_count', 'created_at')
    search_fields = ('name', 'user__username', 'user__telegram_id')
    list_select_related = ('user',)

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'category', 'is_completed',
        'reminder_level', 'deadline', 'next_reminder_time'
    )
    list_filter = ('is_completed', 'reminder_level', 'category')
    search_fields = ('title', 'description', 'user__username', 'user__telegram_id')
    list_select_related = ('user', 'category')
    readonly_fields = ('next_reminder_time', 'last_reminder_sent', 'created_at', 'updated_at')
    date_hierarchy = 'deadline'

    fieldsets = (
        (None, {
            'fields': ('user', 'category', 'title', 'description', 'is_completed')
        }),
        ('Deadline', {
            'fields': ('deadline',)
        }),
        ('Reminders (auto-managed)', {
            'fields': ('reminder_level', 'next_reminder_time', 'last_reminder_sent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
