from django.contrib import admin
from .models import Subscription, AdminAction


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "channel", "tariff", "status", "start_date", "end_date", "remaining_days")
    list_filter = ("status", "channel")
    search_fields = ("user__telegram_id", "user__username", "channel__name")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ("admin_telegram_id", "action", "subscription", "timestamp")
    list_filter = ("action",)
    readonly_fields = ("timestamp",)
