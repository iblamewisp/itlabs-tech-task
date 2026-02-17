from rest_framework.permissions import BasePermission
from django.conf import settings


class InternalAPIKeyPermission(BasePermission):
    """Only allow requests that carry the shared internal API key."""

    def has_permission(self, request, view):
        expected = getattr(settings, 'INTERNAL_API_KEY', '')
        if not expected:
            return True  # key not configured — open in dev
        return request.headers.get('X-Internal-Key') == expected
