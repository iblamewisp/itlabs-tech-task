# apps/tasks/views.py
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from apps.users.models import User
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer
from .services.task_service import TaskService


class TaskPagination(PageNumberPagination):
    """Custom pagination for tasks"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tasks.
    Only handles HTTP logic, delegates to TaskService.
    """
    serializer_class = TaskSerializer
    pagination_class = TaskPagination

    def get_queryset(self):
        telegram_id = self.request.query_params.get('telegram_id')

        if not telegram_id:
            raise ValidationError({'telegram_id': 'Required in query params'})

        user = get_object_or_404(User, telegram_id=telegram_id)

        queryset = Task.objects.filter(user=user).select_related('category')

        # Filter by completion status if provided
        is_completed = self.request.query_params.get('is_completed')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')

        return queryset
    
    def perform_create(self, serializer):
        """Delegate to TaskService"""
        telegram_id = self.request.query_params.get('telegram_id')
        
        if not telegram_id:
            raise ValidationError({'telegram_id': 'Required in query params'})
        
        user = get_object_or_404(User, telegram_id=telegram_id)
        
        # Delegate to service
        task = TaskService.create_task(
            user=user,
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            category=serializer.validated_data.get('category'),
            deadline=serializer.validated_data.get('deadline')
        )
        
        # Set instance for serializer response
        serializer.instance = task
    
    def perform_update(self, serializer):
        """Handle task updates - delegate to TaskService"""
        instance = serializer.instance
        validated_data = serializer.validated_data

        # Check if completion status changed
        is_completed_changed = 'is_completed' in validated_data and validated_data['is_completed'] != instance.is_completed

        # Use TaskService for updates to ensure reminders are handled
        updated_task = TaskService.update_task(
            task=instance,
            title=validated_data.get('title'),
            description=validated_data.get('description'),
            category=validated_data.get('category'),
            deadline=validated_data.get('deadline'),
        )

        # Handle completion status separately
        if is_completed_changed:
            if validated_data['is_completed']:
                updated_task = TaskService.complete_task(updated_task)
            else:
                updated_task = TaskService.uncomplete_task(updated_task)

        # Set instance for serializer response
        serializer.instance = updated_task


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        telegram_id = self.request.query_params.get('telegram_id')
        
        if not telegram_id:
            raise ValidationError({'telegram_id': 'Required in query params'})
        
        user = get_object_or_404(User, telegram_id=telegram_id)
        return Category.objects.filter(user=user)
    
    def perform_create(self, serializer):
        telegram_id = self.request.query_params.get('telegram_id')
        
        if not telegram_id:
            raise ValidationError({'telegram_id': 'Required in query params'})
        
        user = get_object_or_404(User, telegram_id=telegram_id)
        serializer.save(user=user)