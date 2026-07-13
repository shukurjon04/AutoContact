"""Async wrappers for subscription operations."""
from asgiref.sync import sync_to_async
from apps.subscriptions.models import Subscription
from django.utils import timezone


@sync_to_async
def get_user_active_subscriptions(telegram_id: int) -> list[Subscription]:
    return list(
        Subscription.objects.filter(
            user__telegram_id=telegram_id,
            status=Subscription.Status.ACTIVE,
            end_date__gt=timezone.now(),
        )
        .select_related("channel", "tariff")
        .order_by("end_date")
    )
