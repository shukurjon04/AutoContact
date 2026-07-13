from django.contrib import admin
from .models import Channel, Tariff


class TariffInline(admin.TabularInline):
    model = Tariff
    extra = 1
    fields = ("name", "duration_days", "price", "discount_percent", "is_active", "sort_order")


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "telegram_id", "username", "is_active", "bot_is_admin", "created_at")
    list_filter = ("is_active", "bot_is_admin")
    search_fields = ("name", "telegram_id", "username")
    inlines = [TariffInline]


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("name", "channel", "duration_days", "price", "discount_percent", "is_active")
    list_filter = ("is_active", "channel")
    search_fields = ("name", "channel__name")
