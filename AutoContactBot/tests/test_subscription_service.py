"""
SubscriptionManager service tests.
"""
import pytest
from datetime import timedelta
from django.utils import timezone
from apps.users.models import TelegramUser
from apps.channels.models import Channel, Tariff
from apps.subscriptions.models import Subscription
from apps.subscriptions.services import SubscriptionManager


@pytest.fixture
def tg_user(db):
    return TelegramUser.objects.create(
        telegram_id=123456789,
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def channel(db):
    return Channel.objects.create(
        name="Test Channel",
        telegram_id=-1001234567890,
        is_active=True,
        bot_is_admin=True,
    )


@pytest.fixture
def tariff(db, channel):
    return Tariff.objects.create(
        channel=channel,
        name="1 oylik",
        duration_days=30,
        price=50000,
        is_active=True,
    )


@pytest.mark.django_db
def test_activate_creates_new_subscription(tg_user, channel, tariff):
    sub, is_new = SubscriptionManager.activate(
        user=tg_user, channel=channel, tariff=tariff
    )
    assert is_new is True
    assert sub.status == Subscription.Status.ACTIVE
    assert sub.user == tg_user
    assert sub.channel == channel
    # end_date should be ~30 days from now
    expected = timezone.now() + timedelta(days=30)
    diff = abs((sub.end_date - expected).total_seconds())
    assert diff < 5  # within 5 seconds


@pytest.mark.django_db
def test_activate_extends_existing_subscription(tg_user, channel, tariff):
    # Create initial subscription
    sub1, is_new1 = SubscriptionManager.activate(
        user=tg_user, channel=channel, tariff=tariff
    )
    assert is_new1 is True
    original_end = sub1.end_date

    # Activate again — should extend
    sub2, is_new2 = SubscriptionManager.activate(
        user=tg_user, channel=channel, tariff=tariff
    )
    assert is_new2 is False
    assert sub2.pk == sub1.pk
    assert sub2.end_date > original_end


@pytest.mark.django_db
def test_expire_subscription(tg_user, channel, tariff):
    sub, _ = SubscriptionManager.activate(
        user=tg_user, channel=channel, tariff=tariff
    )
    SubscriptionManager.expire_subscription(sub)
    sub.refresh_from_db()
    assert sub.status == Subscription.Status.EXPIRED


@pytest.mark.django_db
def test_cancel_subscription(tg_user, channel, tariff):
    sub, _ = SubscriptionManager.activate(
        user=tg_user, channel=channel, tariff=tariff
    )
    SubscriptionManager.cancel_subscription(sub, admin_id=999, note="Test cancel")
    sub.refresh_from_db()
    assert sub.status == Subscription.Status.CANCELLED


@pytest.mark.django_db
def test_get_expired_subscriptions(tg_user, channel, tariff):
    # Create a subscription with past end_date
    past_end = timezone.now() - timedelta(hours=1)
    sub = Subscription.objects.create(
        user=tg_user,
        channel=channel,
        tariff=tariff,
        start_date=timezone.now() - timedelta(days=31),
        end_date=past_end,
        status=Subscription.Status.ACTIVE,
    )
    expired_qs = list(SubscriptionManager.get_expired_subscriptions())
    assert sub in expired_qs
