# apps/users/views.py
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from apps.users.models import User
from apps.users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User operations"""

    serializer_class = UserSerializer
    queryset = User.objects.none()  # empty by default

    def get_queryset(self):
        """
        Filter by telegram_id from query params
        POST doesn't need queryset, everything else does
        """
        # skip queryset for create
        if self.action == 'create':
            return User.objects.none()

        # GET/LIST/RETRIEVE need telegram_id
        telegram_id = self.request.query_params.get('telegram_id')

        if not telegram_id:
            raise ValidationError({'telegram_id': 'Required in query params'})

        return User.objects.filter(telegram_id=telegram_id)

    def perform_create(self, serializer):
        """Create user from telegram_id in body"""
        telegram_id = serializer.validated_data.get('telegram_id')

        # no duplicates
        if User.objects.filter(telegram_id=telegram_id).exists():
            raise ValidationError({'telegram_id': 'User already exists'})

        serializer.save()