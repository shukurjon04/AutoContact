"""Async wrappers for payment operations."""
from asgiref.sync import sync_to_async
from apps.users.models import TelegramUser
from apps.channels.models import Channel, Tariff
from apps.payments.models import Transaction


@sync_to_async
def create_pending_transaction(
    user: TelegramUser,
    tariff_id: int,
    channel_id: int,
    receipt_file_content: bytes,
    file_name: str,
) -> Transaction:
    """
    Transaction yaratadi va unga chek rasmini biriktiradi.
    """
    from django.core.files.base import ContentFile

    tariff = Tariff.objects.get(id=tariff_id, is_active=True)
    channel = Channel.objects.get(id=channel_id, is_active=True)

    transaction = Transaction.objects.create(
        user=user,
        channel=channel,
        tariff=tariff,
        amount=tariff.price_tiyin,
        status=Transaction.Status.PENDING,
    )
    
    transaction.receipt_image.save(file_name, ContentFile(receipt_file_content))
    return transaction


@sync_to_async
def check_payment_status(transaction_id: str) -> str:
    try:
        tx = Transaction.objects.get(id=transaction_id)
        return tx.status
    except Transaction.DoesNotExist:
        return "not_found"


@sync_to_async
def get_user_transaction_history(telegram_id: int, limit: int = 20) -> list[Transaction]:
    return list(
        Transaction.objects.filter(user__telegram_id=telegram_id)
        .select_related("channel", "tariff")
        .order_by("-created_at")[:limit]
    )
