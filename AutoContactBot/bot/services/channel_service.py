"""Async wrappers around Channel/Tariff ORM operations."""
from asgiref.sync import sync_to_async
from apps.channels.models import Channel, Tariff


@sync_to_async
def get_active_channels() -> list[Channel]:
    return list(Channel.objects.filter(is_active=True).order_by("name"))


@sync_to_async
def get_channel_tariffs(channel_id: int) -> list[Tariff]:
    return list(
        Tariff.objects.filter(
            channel_id=channel_id,
            is_active=True,
        )
        .select_related("channel")
        .order_by("sort_order", "duration_days")
    )
