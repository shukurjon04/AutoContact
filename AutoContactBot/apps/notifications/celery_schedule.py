"""
Celery Beat periodic tasks.
Called from Django management command or auto-registered via AppConfig.ready().
"""
from celery.schedules import crontab


CELERYBEAT_SCHEDULE = {
    # Har 5 daqiqada obuna tugash eslatmalarini yuborish
    "check-expiring-subscriptions": {
        "task": "notifications.check_expiring_subscriptions",
        "schedule": crontab(minute="*/5"),
    },
    # Har 5 daqiqada muddati tugagan foydalanuvchilarni kanaldan chiqarish
    "kick-expired-subscribers": {
        "task": "notifications.kick_expired_subscribers",
        "schedule": crontab(minute="*/5"),
    },
}
