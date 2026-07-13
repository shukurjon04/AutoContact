"""Serializers for REST API — barcha modellar uchun."""
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Count, Sum

from apps.users.models import TelegramUser
from apps.channels.models import Channel, Tariff
from apps.subscriptions.models import Subscription, AdminAction
from apps.payments.models import Transaction
from apps.notifications.models import Broadcast, BroadcastRecipient
from apps.core.models import PaymentSettings


# ============================================================================
# TELEGRAM USERS
# ============================================================================

class TelegramUserSerializer(serializers.ModelSerializer):
    """Telegram foydalanuvchisi."""
    full_name = serializers.CharField(read_only=True)
    active_subscriptions_count = serializers.SerializerMethodField()

    class Meta:
        model = TelegramUser
        fields = [
            'id', 'telegram_id', 'username', 'first_name', 'last_name',
            'full_name', 'is_bot_blocked', 'is_active', 'language_code',
            'registered_at', 'updated_at', 'active_subscriptions_count'
        ]
        read_only_fields = ['id', 'registered_at', 'updated_at']

    def get_active_subscriptions_count(self, obj):
        return obj.subscriptions.filter(
            status=Subscription.Status.ACTIVE,
            end_date__gt=timezone.now()
        ).count()


class TelegramUserDetailSerializer(TelegramUserSerializer):
    """Extended info with subscriptions."""
    subscriptions = serializers.SerializerMethodField()
    total_spent_uzs = serializers.SerializerMethodField()

    class Meta(TelegramUserSerializer.Meta):
        fields = TelegramUserSerializer.Meta.fields + [
            'subscriptions', 'total_spent_uzs'
        ]

    def get_subscriptions(self, obj):
        subs = obj.subscriptions.all()
        return SubscriptionListSerializer(subs, many=True).data

    def get_total_spent_uzs(self, obj):
        total = obj.transactions.filter(
            status=Transaction.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        return total // 100


# ============================================================================
# CHANNELS & TARIFFS
# ============================================================================

class TariffSerializer(serializers.ModelSerializer):
    """Kanal uchun narx va muddat."""
    final_price = serializers.FloatField(read_only=True)
    price_tiyin = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tariff
        fields = [
            'id', 'channel', 'name', 'duration_days', 'price',
            'final_price', 'price_tiyin', 'discount_percent',
            'is_active', 'sort_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChannelSerializer(serializers.ModelSerializer):
    """Telegram kanali / guruh."""
    tariffs = TariffSerializer(many=True, read_only=True)
    subscribers_count = serializers.SerializerMethodField()
    revenue_uzs = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'telegram_id', 'username', 'description',
            'is_active', 'bot_is_admin', 'created_at', 'updated_at',
            'tariffs', 'subscribers_count', 'revenue_uzs'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_subscribers_count(self, obj):
        return obj.subscriptions.filter(
            status=Subscription.Status.ACTIVE,
            end_date__gt=timezone.now()
        ).values('user').distinct().count()

    def get_revenue_uzs(self, obj):
        revenue = obj.transactions.filter(
            status=Transaction.Status.PAID
        ).aggregate(total=Sum('amount'))['total'] or 0
        return revenue // 100


class ChannelDetailSerializer(ChannelSerializer):
    """Extended channel info."""
    pass


# ============================================================================
# SUBSCRIPTIONS
# ============================================================================

class SubscriptionListSerializer(serializers.ModelSerializer):
    """Obuna ro'yxat uchun."""
    user = TelegramUserSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    remaining_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'channel', 'tariff', 'status',
            'start_date', 'end_date', 'is_active', 'remaining_days',
            'reminder_sent', 'extended_by_admin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionDetailSerializer(SubscriptionListSerializer):
    """Extended subscription info."""
    admin_actions = serializers.SerializerMethodField()
    transactions = serializers.SerializerMethodField()

    class Meta(SubscriptionListSerializer.Meta):
        fields = SubscriptionListSerializer.Meta.fields + [
            'invite_link_sent', 'invite_link_delivery_status',
            'admin_note', 'admin_actions', 'transactions'
        ]

    def get_admin_actions(self, obj):
        actions = obj.admin_actions.all()
        return AdminActionSerializer(actions, many=True).data

    def get_transactions(self, obj):
        txns = obj.transactions.all()
        return TransactionListSerializer(txns, many=True).data


class SubscriptionCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/update subscriptions."""
    class Meta:
        model = Subscription
        fields = [
            'user', 'channel', 'tariff', 'status',
            'start_date', 'end_date', 'admin_note'
        ]


class AdminActionSerializer(serializers.ModelSerializer):
    """Admin tomonidan qilingan amallar."""
    class Meta:
        model = AdminAction
        fields = [
            'id', 'admin_telegram_id', 'subscription', 'action',
            'details', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


# ============================================================================
# PAYMENTS / TRANSACTIONS
# ============================================================================

class TransactionListSerializer(serializers.ModelSerializer):
    """Tranzaksiya ro'yxat uchun."""
    user = TelegramUserSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)
    amount_uzs = serializers.IntegerField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'channel', 'tariff', 'amount',
            'amount_uzs', 'status', 'created_at', 'paid_at',
            'cancelled_at', 'cancel_reason'
        ]
        read_only_fields = [
            'id', 'created_at', 'paid_at', 'cancelled_at'
        ]


class TransactionDetailSerializer(TransactionListSerializer):
    """Extended transaction info."""
    subscription = SubscriptionListSerializer(read_only=True)

    class Meta(TransactionListSerializer.Meta):
        fields = TransactionListSerializer.Meta.fields + [
            'subscription', 'receipt_image'
        ]


class TransactionApproveSerializer(serializers.Serializer):
    """Tranzaksiyani tasdiqlash uchun."""
    status = serializers.ChoiceField(
        choices=['paid', 'cancelled'],
        help_text="Tranzaksiya statusini o'zgartirish"
    )
    cancel_reason = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Bekor qilish sababi"
    )


# ============================================================================
# BROADCASTS
# ============================================================================

class BroadcastRecipientSerializer(serializers.ModelSerializer):
    """Broadcast qabul qiluvchisi."""
    user = TelegramUserSerializer(read_only=True)

    class Meta:
        model = BroadcastRecipient
        fields = ['id', 'broadcast', 'user', 'status', 'created_at']
        read_only_fields = ['id', 'broadcast', 'created_at']


class BroadcastListSerializer(serializers.ModelSerializer):
    """Broadcast ro'yxat uchun."""
    target_channel = ChannelSerializer(read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Broadcast
        fields = [
            'id', 'text', 'target_type', 'target_channel', 'status',
            'total_count', 'sent_count', 'failed_count', 'progress_percent',
            'created_by', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at', 'total_count',
                           'sent_count', 'failed_count']

    def get_progress_percent(self, obj):
        if obj.total_count == 0:
            return 0
        return int((obj.sent_count / obj.total_count) * 100)


class BroadcastDetailSerializer(BroadcastListSerializer):
    """Extended broadcast info."""
    recipients = BroadcastRecipientSerializer(many=True, read_only=True)

    class Meta(BroadcastListSerializer.Meta):
        fields = BroadcastListSerializer.Meta.fields + ['recipients', 'photo']


class BroadcastCreateSerializer(serializers.ModelSerializer):
    """Create broadcast."""
    class Meta:
        model = Broadcast
        fields = [
            'text', 'photo', 'target_type', 'target_channel',
            'expiring_days', 'created_by'
        ]


class BroadcastSendSerializer(serializers.Serializer):
    """Send broadcast (start broadcasting)."""
    pass  # No additional fields needed


# ============================================================================
# PAYMENT SETTINGS
# ============================================================================

class PaymentSettingsSerializer(serializers.ModelSerializer):
    """To'lov sozlamalari."""
    class Meta:
        model = PaymentSettings
        fields = ['card_number', 'card_owner']


# ============================================================================
# DASHBOARD STATS
# ============================================================================

class DashboardStatsSerializer(serializers.Serializer):
    """Dashboard statistics."""
    active_subscribers = serializers.IntegerField()
    monthly_revenue_uzs = serializers.IntegerField()
    expiring_7d = serializers.IntegerField()
    stale_pending = serializers.IntegerField()
    today_revenue_uzs = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_channels = serializers.IntegerField()


class BroadcastStatusSerializer(serializers.Serializer):
    """Real-time broadcast progress."""
    status = serializers.CharField()
    total_count = serializers.IntegerField()
    sent_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    progress_percent = serializers.IntegerField()
