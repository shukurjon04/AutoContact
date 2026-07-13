from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "channel", "tariff", "amount_uzs", "status", "created_at", "paid_at", "receipt_preview")
    list_filter = ("status", "channel")
    list_editable = ("status",)
    search_fields = ("user__telegram_id", "user__username")
    readonly_fields = ("id", "created_at", "paid_at", "cancelled_at")

    def receipt_preview(self, obj):
        if obj.receipt_image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.receipt_image.url)
        return "Yo'q"
    receipt_preview.short_description = "Chek rasmi"

    fieldsets = (
        (None, {
            "fields": ("user", "channel", "tariff", "subscription", "amount", "status", "receipt_image", "receipt_preview")
        }),
        ("Vaqtlar", {
            "fields": ("created_at", "paid_at", "cancelled_at", "cancel_reason"),
            "classes": ("collapse",),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        fields.append("receipt_preview")
        return fields
