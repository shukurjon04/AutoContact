"""
Channel and Tariff models.
"""
from django.db import models
from django.core.validators import MinValueValidator


class Channel(models.Model):
    """Telegram kanali yoki yopiq guruhi."""

    name = models.CharField(max_length=255)
    telegram_id = models.BigIntegerField(
        unique=True,
        help_text="Telegram chat ID (e.g. -100123456789)",
    )
    username = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="@username without @",
    )
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    bot_is_admin = models.BooleanField(
        default=False,
        help_text="Verified bot admin status via Telegram API",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "channels"
        verbose_name = "Kanal / Guruh"
        verbose_name_plural = "Kanallar / Guruhlar"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def deactivate(self) -> None:
        """Kanal va uning barcha tariflarini o'chirish."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])
        self.tariffs.filter(is_active=True).update(is_active=False)


class Tariff(models.Model):
    """Obuna tarifi — kanal uchun narx va muddat."""

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="tariffs",
    )
    name = models.CharField(max_length=255, help_text="Masalan: '1 oylik', '3 oylik'")
    duration_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Obuna muddati kunlarda",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(100)],
        help_text="Narxi UZS da (minimum 100 so'm)",
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Chegirma foizi (0–100)",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tariffs"
        verbose_name = "Tarif"
        verbose_name_plural = "Tariflar"
        ordering = ["channel", "sort_order", "duration_days"]

    def __str__(self) -> str:
        return f"{self.channel.name} — {self.name} ({self.final_price:,.0f} UZS)"

    @property
    def price_tiyin(self) -> int:
        """Payme API 1 UZS = 100 tiyin formatida qaytaradi."""
        return int(self.final_price * 100)

    @property
    def final_price(self):
        """Chegirma hisobga olingan narx."""
        if self.discount_percent:
            return self.price * (1 - self.discount_percent / 100)
        return self.price
