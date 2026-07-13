"""
Subscription models — tracks user memberships in channels.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.users.models import TelegramUser
from apps.channels.models import Channel, Tariff


class Subscription(models.Model):
    """Foydalanuvchi obunasi."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Faol"
        EXPIRED = "expired", "Muddati tugagan"
        CANCELLED = "cancelled", "Bekor qilingan"

    class ReminderSent(models.TextChoices):
        NONE = "none", "Yuborilmagan"
        THREE_DAYS = "3d", "3 kun qolganida"
        ONE_DAY = "1d", "1 kun qolganida"
        ONE_HOUR = "1h", "1 soat qolganida"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.SET_NULL,
        null=True,
        related_name="subscriptions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(db_index=True)
    invite_link_sent = models.BooleanField(default=False)
    invite_link_delivery_status = models.CharField(
        max_length=20,
        choices=[("sent", "Yuborildi"), ("failed", "Yuborilmadi"), ("pending", "Kutilmoqda")],
        default="pending",
    )
    reminder_sent = models.CharField(
        max_length=10,
        choices=ReminderSent.choices,
        default=ReminderSent.NONE,
    )
    # Manual extension tracking
    extended_by_admin = models.BooleanField(default=False)
    admin_note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"
        verbose_name = "Obuna"
        verbose_name_plural = "Obunalar"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "channel", "status"]),
            models.Index(fields=["status", "end_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.channel.name} ({self.status})"

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE and self.end_date > timezone.now()

    @property
    def remaining_days(self) -> int:
        if not self.is_active:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    @property
    def days_left(self) -> int:
        """Qolgan kunlar soni (remaining_days ning aliasi)."""
        if self.status != self.Status.ACTIVE:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    def extend(self, days: int, admin_id: int | None = None, note: str = "") -> None:
        """Obuna muddatini uzaytirish."""
        from datetime import timedelta
        self.end_date = self.end_date + timedelta(days=days)
        if admin_id:
            self.extended_by_admin = True
            self.admin_note = note
        self.status = self.Status.ACTIVE
        self.save(update_fields=["end_date", "extended_by_admin", "admin_note", "status", "updated_at"])


class AdminAction(models.Model):
    """Admin tomonidan qilingan qo'lda amallar log."""

    class ActionType(models.TextChoices):
        EXTEND = "extend", "Muddatni uzaytirish"
        CANCEL = "cancel", "Obunani bekor qilish"
        KICK = "kick", "Guruhdan chiqarish"
        GRANT = "grant", "Bepul obuna berish"

    admin_telegram_id = models.BigIntegerField()
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        related_name="admin_actions",
    )
    action = models.CharField(max_length=20, choices=ActionType.choices)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin_actions"
        verbose_name = "Admin amali"
        verbose_name_plural = "Admin amallari"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"Admin:{self.admin_telegram_id} → {self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"
