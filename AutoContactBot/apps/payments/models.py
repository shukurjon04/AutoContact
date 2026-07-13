"""
Transaction model — Payme to'lov yozuvlari.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.users.models import TelegramUser
from apps.channels.models import Channel, Tariff
from apps.subscriptions.models import Subscription


class Transaction(models.Model):
    """Foydalanuvchi orqali amalga oshirilgan to'lov (chek orqali)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PAID = "paid", "To'landi"
        CANCELLED = "cancelled", "Bekor qilindi"
        FAILED = "failed", "Muvaffaqiyatsiz"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions",
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    # Payme fields o'rniga Chek rasmi
    receipt_image = models.ImageField(
        upload_to="receipts/",
        null=True,
        blank=True,
        help_text="Foydalanuvchi yuborgan to'lov cheki rasmi",
    )
    amount = models.BigIntegerField(help_text="Miqdor tiyin da (1 UZS = 100 tiyin)")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "transactions"
        verbose_name = "Tranzaksiya"
        verbose_name_plural = "Tranzaksiyalar"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        amount_uzs = self.amount_uzs  # Use our property which handles None
        return f"Transaction {self.id} | {self.user} | {amount_uzs:,} UZS | {self.status}"

    @property
    def amount_uzs(self) -> int:
        if self.amount is None:
            return 0
        return self.amount // 100

