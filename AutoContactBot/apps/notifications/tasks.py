"""
Celery tasks:
- activate_subscription_task   — to'lov tasdiqlangach obuna faollashtirish
- check_expiring_subscriptions — har 5 daqiqada tugash eslatmalari
- kick_expired_subscribers     — har 5 daqiqada muddati tugaganlarni chiqarish
- send_broadcast_task          — ommaviy xabarnoma yuborish
"""
import asyncio
import logging
import time

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# ---------------------------------------------------------------------------
# Helper: event loop-safe asyncio.run replacement for Celery workers
# ---------------------------------------------------------------------------
def _run_async(coro):
    """Celery worker thread ichida async coroutine ni xavfsiz bajaradi."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
            asyncio.set_event_loop(None)


# ---------------------------------------------------------------------------
# 1. Subscription activation after successful payment
# ---------------------------------------------------------------------------
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="notifications.activate_subscription",
)
def activate_subscription_task(self, transaction_id: str):
    """
    To'lov tasdiqlangach obunani faollashtiradi va invite link yuboradi.
    """
    from apps.payments.models import Transaction
    from apps.subscriptions.services import SubscriptionManager
    from apps.notifications.telegram_sender import TelegramSender

    try:
        transaction = Transaction.objects.select_related(
            "user", "channel", "tariff"
        ).get(id=transaction_id)
    except Transaction.DoesNotExist:
        logger.error("activate_subscription_task: Transaction not found: %s", transaction_id)
        return
    except Exception as exc:
        logger.exception("activate_subscription_task: unexpected error fetching transaction")
        raise self.retry(exc=exc)

    try:
        subscription, is_new = SubscriptionManager.activate(
            user=transaction.user,
            channel=transaction.channel,
            tariff=transaction.tariff,
        )

        # Link transaction → subscription
        transaction.subscription = subscription
        transaction.save(update_fields=["subscription"])

        sender = TelegramSender()

        if is_new:
            # Retry invite link creation up to 3 times
            invite_link = None
            for attempt in range(3):
                invite_link = _run_async(
                    sender.create_invite_link(channel_id=transaction.channel.telegram_id)
                )
                if invite_link:
                    break
                logger.warning(
                    "invite_link attempt %d failed for sub %s", attempt + 1, subscription.id
                )
                time.sleep(5)

            if invite_link:
                _run_async(
                    sender.send_invite_link(
                        user_telegram_id=transaction.user.telegram_id,
                        channel_name=transaction.channel.name,
                        invite_link=invite_link,
                        end_date=subscription.end_date,
                    )
                )
                subscription.invite_link_sent = True
                subscription.invite_link_delivery_status = "sent"
            else:
                subscription.invite_link_delivery_status = "failed"
                logger.error(
                    "Failed to create invite link after 3 attempts for sub %s", subscription.id
                )
        else:
            # Obuna uzaytirildi — faqat xabar yuborish kerak
            _run_async(
                sender.send_subscription_extended(
                    user_telegram_id=transaction.user.telegram_id,
                    channel_name=transaction.channel.name,
                    end_date=subscription.end_date,
                )
            )
            subscription.invite_link_sent = True
            subscription.invite_link_delivery_status = "sent"

        subscription.save(update_fields=["invite_link_sent", "invite_link_delivery_status"])
        logger.info(
            "activate_subscription_task done: sub=%s new=%s", subscription.id, is_new
        )

    except Exception as exc:
        logger.exception(
            "activate_subscription_task error for transaction %s", transaction_id
        )
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# 2. Expiry reminders — runs every 5 min via Celery Beat
# ---------------------------------------------------------------------------
@shared_task(name="notifications.check_expiring_subscriptions")
def check_expiring_subscriptions():
    """
    Obuna tugash eslatmalarini yuboradi:
      - 3 kun qolsa
      - 1 kun qolsa
      - 1 soat qolsa
    Har bir interval faqat bir marta yuboriladi (reminder_sent field orqali).
    """
    from apps.subscriptions.models import Subscription
    from apps.subscriptions.services import SubscriptionManager
    from apps.notifications.telegram_sender import TelegramSender

    sender = TelegramSender()

    # (minutes_from, minutes_to, reminder_key, label)
    # Har bir window ± 5 daqiqa aniqlikda
    WINDOWS = [
        (4315, 4325, Subscription.ReminderSent.THREE_DAYS, "3 kun"),
        (1435, 1445, Subscription.ReminderSent.ONE_DAY,    "1 kun"),
        (55,   65,   Subscription.ReminderSent.ONE_HOUR,   "1 soat"),
    ]

    total_sent = 0

    for minutes_from, minutes_to, reminder_key, label in WINDOWS:
        subs = list(
            SubscriptionManager.get_active_subscriptions_expiring_in(minutes_from, minutes_to)
        )
        for sub in subs:
            # Faqat o'sha intervalga tegishli eslatmani yuborish
            already_sent = {
                Subscription.ReminderSent.THREE_DAYS: sub.reminder_sent != Subscription.ReminderSent.NONE,
                Subscription.ReminderSent.ONE_DAY:    sub.reminder_sent in (
                    Subscription.ReminderSent.ONE_DAY,
                    Subscription.ReminderSent.ONE_HOUR,
                ),
                Subscription.ReminderSent.ONE_HOUR:   sub.reminder_sent == Subscription.ReminderSent.ONE_HOUR,
            }

            if already_sent.get(reminder_key, False):
                continue

            try:
                _run_async(
                    sender.send_expiry_reminder(
                        user_telegram_id=sub.user.telegram_id,
                        channel_name=sub.channel.name,
                        end_date=sub.end_date,
                        time_left_label=label,
                        subscription_id=str(sub.id),
                    )
                )
                sub.reminder_sent = reminder_key
                sub.save(update_fields=["reminder_sent"])
                total_sent += 1
            except Exception:
                logger.exception(
                    "check_expiring_subscriptions: failed to send reminder sub=%s", sub.id
                )

    logger.info("check_expiring_subscriptions: sent=%d", total_sent)
    return total_sent


# ---------------------------------------------------------------------------
# 3. Kick expired subscribers — runs every 5 min via Celery Beat
# ---------------------------------------------------------------------------
@shared_task(name="notifications.kick_expired_subscribers")
def kick_expired_subscribers():
    """Muddati tugagan foydalanuvchilarni kanaldan chiqaradi."""
    from apps.subscriptions.services import SubscriptionManager
    from apps.notifications.telegram_sender import TelegramSender

    expired = list(SubscriptionManager.get_expired_subscriptions())
    sender = TelegramSender()
    kicked = 0

    for sub in expired:
        try:
            # DB da expired deb belgilash
            SubscriptionManager.expire_subscription(sub)

            # Telegram: ban + unban
            success = _run_async(
                sender.kick_user(
                    channel_id=sub.channel.telegram_id,
                    user_id=sub.user.telegram_id,
                )
            )

            if success:
                kicked += 1
                # Foydalanuvchiga xabar yuborish
                _run_async(
                    sender.send_subscription_expired(
                        user_telegram_id=sub.user.telegram_id,
                        channel_name=sub.channel.name,
                        subscription_id=str(sub.id),
                    )
                )
            else:
                logger.error(
                    "kick_expired_subscribers: kick failed sub=%s user=%s",
                    sub.id,
                    sub.user.telegram_id,
                )

        except Exception:
            logger.exception(
                "kick_expired_subscribers: error processing sub=%s", sub.id
            )

    logger.info("kick_expired_subscribers: kicked=%d", kicked)
    return kicked


# ---------------------------------------------------------------------------
# 4. Broadcast — rate-limited at 30 msg/sec (Telegram limit)
# ---------------------------------------------------------------------------
@shared_task(
    bind=True,
    name="notifications.send_broadcast",
)
def send_broadcast_task(self, broadcast_id: int):
    """Broadcast xabarlarini Celery orqali yuboradi. Max 30 msg/sec."""
    from apps.notifications.models import Broadcast, BroadcastRecipient
    from apps.notifications.telegram_sender import TelegramSender
    from django.conf import settings

    try:
        broadcast = Broadcast.objects.get(id=broadcast_id)
    except Broadcast.DoesNotExist:
        logger.error("send_broadcast_task: Broadcast not found id=%s", broadcast_id)
        return

    sender = TelegramSender()
    recipients = list(
        BroadcastRecipient.objects.filter(
            broadcast=broadcast,
            status=BroadcastRecipient.Status.PENDING,
        ).select_related("user")
    )

    RATE_SLEEP = 1 / 29  # ~0.034s → slightly under 30/s to stay safe

    for recipient in recipients:
        try:
            _run_async(
                sender.send_broadcast_message(
                    user_telegram_id=recipient.user.telegram_id,
                    text=broadcast.text,
                    photo_url=(
                        f"{settings.WEBHOOK_HOST.rstrip('/')}{broadcast.photo.url}"
                        if broadcast.photo else None
                    ),
                )
            )
            recipient.status = BroadcastRecipient.Status.SENT
        except Exception as exc:
            logger.warning(
                "send_broadcast_task: failed user=%s err=%s",
                recipient.user.telegram_id,
                exc,
            )
            recipient.status = BroadcastRecipient.Status.FAILED

        recipient.save(update_fields=["status"])
        time.sleep(RATE_SLEEP)

    # Final stats
    sent_count = BroadcastRecipient.objects.filter(
        broadcast=broadcast, status=BroadcastRecipient.Status.SENT
    ).count()
    failed_count = BroadcastRecipient.objects.filter(
        broadcast=broadcast, status=BroadcastRecipient.Status.FAILED
    ).count()

    broadcast.sent_count = sent_count
    broadcast.failed_count = failed_count
    broadcast.status = Broadcast.Status.COMPLETED
    broadcast.save(update_fields=["sent_count", "failed_count", "status"])

    logger.info(
        "send_broadcast_task: id=%s sent=%d failed=%d",
        broadcast_id, sent_count, failed_count,
    )


# ---------------------------------------------------------------------------
# 5. Manual Payment Approval Notification
# ---------------------------------------------------------------------------
@shared_task(name="notifications.notify_user_about_payment_status")
def notify_user_about_payment_status(user_telegram_id: int, status: str, channel_name: str):
    """
    To'lov tasdiqlanganda yoki bekor qilinganda foydalanuvchiga xabar yuboradi.
    """
    from apps.notifications.telegram_sender import TelegramSender

    sender = TelegramSender()

    if status == "approved":
        text = (
            f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            f"<b>{channel_name}</b> kanali uchun obunangiz faollashtirildi.\n"
            f"Kanalga kirish uchun pastdagi <i>Kanalga kirish</i> tugmasini bosing (bot yuborgan xabarlardan birida)."
        )
    else:
        text = (
            f"❌ <b>To'lovingiz bekor qilindi.</b>\n\n"
            f"<b>{channel_name}</b> kanali uchun yuborgan to'lov chekingiz tasdiqlanmadi.\n"
            f"Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning."
        )

    try:
        _run_async(
            sender.send_broadcast_message(
                user_telegram_id=user_telegram_id,
                text=text,
            )
        )
        logger.info("Payment notification sent to %s for channel %s (status: %s)", user_telegram_id, channel_name, status)
    except Exception as exc:
        logger.exception("Failed to send payment notification to %s: %s", user_telegram_id, exc)
