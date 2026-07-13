"""Main URL configuration - API Only."""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Health check
    path("health/", include("apps.core.urls.health")),

    # Payme Webhook
    path("payme/", include("apps.payments.urls")),

    # REST API (main interface)
    path("api/v1/", include("apps.api.urls")),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
