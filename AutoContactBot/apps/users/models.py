"""
TelegramUser model — represents a bot user registered via /start command.
"""
from django.db import models
from django.utils import timezone


class TelegramUser(models.Model):
    """Telegram foydalanuvchisi."""

    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=128, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, default="")
    last_name = models.CharField(max_length=255, blank=True, default="")
    is_bot_blocked = models.BooleanField(
        default=False,
        help_text="True if the user has blocked the bot",
    )
    is_active = models.BooleanField(default=True)
    language_code = models.CharField(max_length=10, default="uz")
    registered_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "telegram_users"
        verbose_name = "Telegram foydalanuvchi"
        verbose_name_plural = "Telegram foydalanuvchilar"
        ordering = ["-registered_at"]

    def __str__(self) -> str:
        name = self.full_name or f"id:{self.telegram_id}"
        username = f" (@{self.username})" if self.username else ""
        return f"{name}{username}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def update_from_telegram(
        self,
        first_name: str = "",
        last_name: str = "",
        username: str | None = None,
        language_code: str = "uz",
    ) -> None:
        """Update user fields from Telegram data."""
        self.first_name = first_name
        self.last_name = last_name or ""
        self.username = username
        self.language_code = language_code
        self.save(update_fields=["first_name", "last_name", "username", "language_code", "updated_at"])
