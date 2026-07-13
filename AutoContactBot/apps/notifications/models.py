"""Broadcast models."""
from django.db import models
from apps.users.models import TelegramUser
from apps.channels.models import Channel


class Broadcast(models.Model):
    """Ommaviy xabarnoma."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Tayyorlanmoqda"
        IN_PROGRESS = "in_progress", "Yuborilmoqda"
        COMPLETED = "completed", "Yakunlandi"
        FAILED = "failed", "Xatolik"

    class TargetType(models.TextChoices):
        ALL = "all", "Barcha foydalanuvchilar"
        CHANNEL = "channel", "Kanal obunachilari"
        EXPIRING = "expiring", "Muddati tugayotganlar"

    text = models.TextField(max_length=4096)
    photo = models.ImageField(upload_to="broadcasts/", null=True, blank=True)
    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices,
        default=TargetType.ALL,
    )
    target_channel = models.ForeignKey(
        Channel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="broadcasts",
    )
    expiring_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Agar target_type=expiring bo'lsa, necha kun ichida tugaydigan obunalar",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_by = models.CharField(max_length=128, default="admin")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "broadcasts"
        verbose_name = "Broadcast"
        verbose_name_plural = "Broadcastlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Broadcast #{self.id} ({self.status}) — {self.created_at:%Y-%m-%d}"


class BroadcastRecipient(models.Model):
    """Broadcast qabul qiluvchi."""

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        SENT = "sent", "Yuborildi"
        FAILED = "failed", "Yuborilmadi"

    broadcast = models.ForeignKey(
        Broadcast,
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="broadcast_receipts",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "broadcast_recipients"
        verbose_name = "Broadcast qabul qiluvchi"
        verbose_name_plural = "Broadcast qabul qiluvchilar"
        unique_together = [("broadcast", "user")]
