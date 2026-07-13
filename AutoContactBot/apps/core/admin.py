"""
Core admin — register PaymentSettings in Django Admin.
"""
from django.contrib import admin
from .models import PaymentSettings


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ("card_number", "card_owner")

    def has_add_permission(self, request):
        # Only one instance allowed
        return not PaymentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
