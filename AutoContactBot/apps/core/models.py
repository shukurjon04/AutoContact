"""
Core models — Singleton settings for payment card details.
"""
from django.db import models


class SingletonModel(models.Model):
    """Abstract model for singleton (only one instance)."""
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class PaymentSettings(SingletonModel):
    """Payment settings: card number, owner name, etc."""
    card_number = models.CharField(
        max_length=20,
        default="8600 0000 0000 0000",
        help_text="Karta raqami (masalan: 8600 1234 5678 9010)"
    )
    card_owner = models.CharField(
        max_length=255,
        default="Falonchi Pistonchiyev",
        help_text="Karta egasining ismi va familyasi"
    )

    class Meta:
        verbose_name = "To'lov sozlamalari"
        verbose_name_plural = "To'lov sozlamalari"

    def __str__(self) -> str:
        return "To'lov sozlamalari"
