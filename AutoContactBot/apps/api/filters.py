"""Custom filters for REST API."""
import django_filters
from apps.channels.models import Channel
from apps.subscriptions.models import Subscription
from apps.payments.models import Transaction
from apps.notifications.models import Broadcast


class ChannelFilter(django_filters.FilterSet):
    """Kanallar uchun filter."""
    is_active = django_filters.BooleanFilter()
    bot_is_admin = django_filters.BooleanFilter()
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Channel
        fields = ['is_active', 'bot_is_admin']


class SubscriptionFilter(django_filters.FilterSet):
    """Obunalar uchun filter."""
    status = django_filters.ChoiceFilter(choices=Subscription.Status.choices)
    user = django_filters.NumberFilter()
    channel = django_filters.NumberFilter()
    start_date_from = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = Subscription
        fields = ['status', 'user', 'channel']


class TransactionFilter(django_filters.FilterSet):
    """Tranzaksiyalar uchun filter."""
    status = django_filters.ChoiceFilter(choices=Transaction.Status.choices)
    user = django_filters.NumberFilter()
    channel = django_filters.NumberFilter()
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['status', 'user', 'channel']


class BroadcastFilter(django_filters.FilterSet):
    """Broadcasts uchun filter."""
    status = django_filters.ChoiceFilter(choices=Broadcast.Status.choices)
    target_type = django_filters.ChoiceFilter(choices=Broadcast.TargetType.choices)
    created_at_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Broadcast
        fields = ['status', 'target_type']
