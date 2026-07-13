from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = "Xabarnomalar"

    def ready(self):
        """Celery Beat periodic tasks ni ro'yxatga olish."""
        from django.conf import settings
        try:
            from celery import current_app
            from apps.notifications.celery_schedule import CELERYBEAT_SCHEDULE
            current_app.conf.beat_schedule.update(CELERYBEAT_SCHEDULE)
        except Exception:
            pass  # Celery hali ishga tushmagan bo'lishi mumkin
