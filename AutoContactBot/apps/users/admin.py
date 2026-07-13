from django.contrib import admin
from django.db.models import Sum
from .models import TelegramUser
from apps.payments.models import Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ("id", "channel", "tariff", "amount_uzs", "status", "receipt_preview", "created_at", "paid_at")
    can_delete = False
    show_change_link = True
    fields = ("id", "channel", "tariff", "amount_uzs", "status", "receipt_preview", "created_at", "paid_at")

    def receipt_preview(self, obj):
        if obj.receipt_image:
            from django.utils.html import format_html
            return format_html(f'<a href="{obj.receipt_image.url}" target="_blank"><img src="{obj.receipt_image.url}" style="max-height: 50px;" /></a>')
        return "Yo'q"
    receipt_preview.short_description = "Chek rasmi"


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "full_name", "username", "is_active", "is_bot_blocked", "registered_at", "total_paid")
    list_filter = ("is_active", "is_bot_blocked")
    search_fields = ("telegram_id", "username", "first_name", "last_name")
    readonly_fields = ("telegram_id", "registered_at", "updated_at", "total_paid")
    ordering = ("-registered_at",)
    inlines = [TransactionInline]

    def total_paid(self, obj):
        total_tiyin = obj.transactions.filter(status=Transaction.Status.PAID).aggregate(Sum("amount"))["amount__sum"]
        if total_tiyin is None:
            return 0
        total_uzs = total_tiyin // 100
        return f"{total_uzs:,} UZS"
    total_paid.short_description = "Umumiy to'langan summa"
    total_paid.admin_order_field = "transactions__amount"
