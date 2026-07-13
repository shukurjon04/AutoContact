from django.contrib import admin
from .models import Broadcast, BroadcastRecipient


class BroadcastRecipientInline(admin.TabularInline):
    model = BroadcastRecipient
    extra = 0
    readonly_fields = ("user", "status", "created_at")
    can_delete = False


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = (
        "id", "target_type", "status",
        "total_count", "sent_count", "failed_count",
        "created_by", "created_at",
    )
    list_filter = ("status", "target_type")
    readonly_fields = ("sent_count", "failed_count", "total_count", "created_at", "sent_at")
    inlines = [BroadcastRecipientInline]


@admin.register(BroadcastRecipient)
class BroadcastRecipientAdmin(admin.ModelAdmin):
    list_display = ("broadcast", "user", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = ("created_at",)
