"""
Management command: setup_periodic_tasks
Celery Beat periodic tasks ni django_celery_beat orqali ma'lumotlar bazasiga yozadi.
Usage: python manage.py setup_periodic_tasks
"""
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = "Celery Beat periodic tasks ni yaratadi yoki yangilaydi."

    def handle(self, *args, **options):
        # 5 daqiqalik interval
        schedule_5min, _ = IntervalSchedule.objects.get_or_create(
            every=5,
            period=IntervalSchedule.MINUTES,
        )

        # Obuna tugash eslatmalari
        task1, created = PeriodicTask.objects.update_or_create(
            name="Obuna tugash eslatmalari (har 5 daqiqa)",
            defaults={
                "task": "notifications.check_expiring_subscriptions",
                "interval": schedule_5min,
                "enabled": True,
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Yaratildi' if created else 'Yangilandi'}: {task1.name}"
            )
        )

        # Muddati tugaganlarni chiqarish
        task2, created = PeriodicTask.objects.update_or_create(
            name="Muddati tugaganlarni kanaldan chiqarish (har 5 daqiqa)",
            defaults={
                "task": "notifications.kick_expired_subscribers",
                "interval": schedule_5min,
                "enabled": True,
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Yaratildi' if created else 'Yangilandi'}: {task2.name}"
            )
        )

        self.stdout.write(self.style.SUCCESS("\nBarcha periodic tasks muvaffaqiyatli sozlandi."))
