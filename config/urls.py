from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """Health check — probes DB and Redis so load balancers get real signal."""
    checks = {}

    try:
        connection.ensure_connection()
        checks['db'] = 'ok'
    except Exception as e:
        return JsonResponse({'status': 'error', 'checks': {'db': str(e)}}, status=503)

    try:
        import redis
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        checks['redis'] = 'ok'
    except Exception as e:
        return JsonResponse({'status': 'error', 'checks': {**checks, 'redis': str(e)}}, status=503)

    return JsonResponse({'status': 'ok', 'checks': checks})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.tasks.urls')),
    path('api/', include('apps.users.urls')),
    path('health/', health_check)
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)