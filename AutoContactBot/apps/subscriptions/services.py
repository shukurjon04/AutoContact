"""
SubscriptionManager — core business logic for subscription lifecycle.
"""
import logging
from datetime import timedelta

from django.utils import timezone
from django.db import transaction

from apps.users.models import TelegramUser
from apps.channels.models import Channel, Tariff
from apps.subscriptions.models import Subscription, AdminAction

logger = logging.getLogger(__name__)


class SubscriptionManager:
    """Obuna hayot aylanishini boshqaradi."""

    @staticmethod
    @transaction.atomic
    def activate(
        user: TelegramUser,
        channel: Channel,
        tariff: Tariff,
    ) -> tuple["Subscription", bool]:
        """
        To'lov tasdiqlangach obunani faollashtiradi.

        Returns:
            (subscription, is_new) — is_new=False means subscription was extended.
        """
        existing = (
            Subscription.objects.filter(
                user=user,
                channel=channel,
                status=Subscription.Status.ACTIVE,
            )
            .select_for_update()
            .first()
        )

        if existing:
            # Obuna bor — muddatni uzaytir
            existing.extend(days=tariff.duration_days)
            logger.info(
                "Subscription extended: user=%s channel=%s days=%s",
                user.telegram_id,
                channel.telegram_id,
                tariff.duration_days,
            )
            return existing, False

        # Yangi obuna yaratish
        end_date = timezone.now() + timedelta(days=tariff.duration_days)
        subscription = Subscription.objects.create(
            user=user,
            channel=channel,
            tariff=tariff,
            start_date=timezone.now(),
            end_date=end_date,
            status=Subscription.Status.ACTIVE,
        )
        logger.info(
            "Subscription created: user=%s channel=%s until=%s",
            user.telegram_id,
            channel.telegram_id,
            end_date.isoformat(),
        )
        return subscription, True

    @staticmethod
    @transaction.atomic
    def expire_subscription(subscription: Subscription) -> None:
        """Obuna muddatini tugat va foydalanuvchini kanaldan chiqar."""
        subscription.status = Subscription.Status.EXPIRED
        subscription.save(update_fields=["status", "updated_at"])
        logger.info(
            "Subscription expired: id=%s user=%s channel=%s",
            subscription.id,
            subscription.user.telegram_id,
            subscription.channel.telegram_id,
        )

    @staticmethod
    @transaction.atomic
    def cancel_subscription(
        subscription: Subscription,
        admin_id: int | None = None,
        note: str = "",
    ) -> None:
        """Admin yoki tizim tomonidan obunani bekor qilish."""
        subscription.status = Subscription.Status.CANCELLED
        subscription.save(update_fields=["status", "updated_at"])

        if admin_id:
            AdminAction.objects.create(
                admin_telegram_id=admin_id,
                subscription=subscription,
                action=AdminAction.ActionType.CANCEL,
                details={"note": note},
            )
        logger.info(
            "Subscription cancelled: id=%s by_admin=%s",
            subscription.id,
            admin_id,
        )

    @staticmethod
    def get_active_subscriptions_expiring_in(
        minutes_from: int,
        minutes_to: int,
    ):
        """Berilgan vaqt oralig'ida tugaydigan obunalarni qaytaradi."""
        now = timezone.now()
        start = now + timedelta(minutes=minutes_from)
        end = now + timedelta(minutes=minutes_to)
        return Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            end_date__gte=start,
            end_date__lte=end,
        ).select_related("user", "channel", "tariff")

    @staticmethod
    def get_expired_subscriptions():
        """Muddati o'tgan lekin hali expired deb belgilanmagan obunalar."""
        return Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            end_date__lte=timezone.now(),
        ).select_related("user", "channel")
