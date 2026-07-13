"""REST API views — complete DRF ViewSets and APIViews."""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.models import TelegramUser
from apps.channels.models import Channel, Tariff
from apps.subscriptions.models import Subscription, AdminAction
from apps.payments.models import Transaction
from apps.notifications.models import Broadcast, BroadcastRecipient
from apps.core.models import PaymentSettings

from .serializers import (
    TelegramUserSerializer, TelegramUserDetailSerializer,
    ChannelSerializer, ChannelDetailSerializer, TariffSerializer,
    SubscriptionListSerializer, SubscriptionDetailSerializer,
    SubscriptionCreateUpdateSerializer, AdminActionSerializer,
    TransactionListSerializer, TransactionDetailSerializer,
    TransactionApproveSerializer,
    BroadcastListSerializer, BroadcastDetailSerializer,
    BroadcastCreateSerializer, BroadcastSendSerializer,
    BroadcastRecipientSerializer,
    PaymentSettingsSerializer,
    DashboardStatsSerializer, BroadcastStatusSerializer
)


# ============================================================================
# AUTHENTICATION & PROFILE
# ============================================================================

class ProfileView(APIView):
    """Get current user profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can access this API"},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser,
        })


# ============================================================================
# TELEGRAM USERS VIEWSET
# ============================================================================

class TelegramUserViewSet(viewsets.ModelViewSet):
    """Telegram foydalanuvchilar uchun API."""
    queryset = TelegramUser.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_bot_blocked', 'language_code']
    search_fields = ['first_name', 'last_name', 'username', 'telegram_id']
    ordering_fields = ['registered_at', 'first_name']
    ordering = ['-registered_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TelegramUserDetailSerializer
        return TelegramUserSerializer

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Foydalanuvchini blok qilish."""
        user = self.get_object()
        user.is_bot_blocked = True
        user.save(update_fields=['is_bot_blocked', 'updated_at'])
        return Response(
            {"message": "User blocked successfully"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Foydalanuvchini blokdan chiqarish."""
        user = self.get_object()
        user.is_bot_blocked = False
        user.save(update_fields=['is_bot_blocked', 'updated_at'])
        return Response(
            {"message": "User unblocked successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================================
# CHANNELS VIEWSET
# ============================================================================

class ChannelViewSet(viewsets.ModelViewSet):
    """Telegram kanallar / guruhlar uchun API."""
    queryset = Channel.objects.prefetch_related('tariffs')
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'bot_is_admin']
    search_fields = ['name', 'username', 'telegram_id']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChannelDetailSerializer
        return ChannelSerializer

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Kanal va barcha tariflarini o'chirish."""
        channel = self.get_object()
        channel.deactivate()
        return Response(
            {"message": "Channel deactivated successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================================
# TARIFFS VIEWSET
# ============================================================================

class TariffViewSet(viewsets.ModelViewSet):
    """Kanal tariflar uchun API."""
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['channel', 'is_active']
    ordering_fields = ['duration_days', 'price', 'sort_order']
    ordering = ['channel', 'sort_order']

    def get_queryset(self):
        channel_id = self.request.query_params.get('channel')
        if channel_id:
            return Tariff.objects.filter(channel_id=channel_id)
        return super().get_queryset()


# ============================================================================
# SUBSCRIPTIONS VIEWSET
# ============================================================================

class SubscriptionViewSet(viewsets.ModelViewSet):
    """Obunalar uchun API."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'channel', 'status']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'channel__name']
    ordering_fields = ['start_date', 'end_date', 'status']
    ordering = ['-start_date']

    def get_queryset(self):
        return Subscription.objects.select_related(
            'user', 'channel', 'tariff'
        ).prefetch_related('admin_actions', 'transactions')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubscriptionDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SubscriptionCreateUpdateSerializer
        return SubscriptionListSerializer

    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        """Obuna muddatini uzaytirish."""
        subscription = self.get_object()
        days = request.data.get('days', 30)
        note = request.data.get('note', '')

        try:
            days = int(days)
            if days <= 0:
                return Response(
                    {"error": "Days must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid days value"},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.extend(days=days, admin_id=request.user.id, note=note)

        AdminAction.objects.create(
            admin_telegram_id=request.user.id,
            subscription=subscription,
            action=AdminAction.ActionType.EXTEND,
            details={"days": days, "note": note}
        )

        serializer = SubscriptionDetailSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Obunani bekor qilish."""
        subscription = self.get_object()
        reason = request.data.get('reason', '')

        subscription.status = Subscription.Status.CANCELLED
        subscription.save(update_fields=['status', 'updated_at'])

        AdminAction.objects.create(
            admin_telegram_id=request.user.id,
            subscription=subscription,
            action=AdminAction.ActionType.CANCEL,
            details={"reason": reason}
        )

        serializer = SubscriptionDetailSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# TRANSACTIONS VIEWSET
# ============================================================================

class TransactionViewSet(viewsets.ModelViewSet):
    """Tranzaksiyalar uchun API."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'channel', 'status']
    search_fields = ['user__first_name', 'user__last_name', 'channel__name']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return Transaction.objects.select_related(
            'user', 'channel', 'tariff', 'subscription'
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TransactionDetailSerializer
        return TransactionListSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Tranzaksiyani tasdiqlash."""
        transaction = self.get_object()

        if transaction.status != Transaction.Status.PENDING:
            return Response(
                {"error": f"Cannot approve transaction with status {transaction.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction.status = Transaction.Status.PAID
        transaction.paid_at = timezone.now()
        transaction.save(update_fields=['status', 'paid_at', 'updated_at'])

        serializer = TransactionDetailSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Tranzaksiyani rad qilish."""
        transaction = self.get_object()
        reason = request.data.get('reason', '')

        if transaction.status != Transaction.Status.PENDING:
            return Response(
                {"error": f"Cannot reject transaction with status {transaction.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction.status = Transaction.Status.CANCELLED
        transaction.cancelled_at = timezone.now()
        transaction.cancel_reason = reason
        transaction.save(update_fields=['status', 'cancelled_at', 'cancel_reason', 'updated_at'])

        serializer = TransactionDetailSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Tranzaksiya statistikasi."""
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        stats = {
            "total_transactions": Transaction.objects.count(),
            "pending_count": Transaction.objects.filter(status=Transaction.Status.PENDING).count(),
            "paid_count": Transaction.objects.filter(status=Transaction.Status.PAID).count(),
            "cancelled_count": Transaction.objects.filter(status=Transaction.Status.CANCELLED).count(),
            "monthly_revenue_uzs": (
                Transaction.objects.filter(
                    status=Transaction.Status.PAID,
                    paid_at__gte=month_start
                ).aggregate(total=Sum('amount'))['total'] or 0
            ) // 100,
        }
        return Response(stats, status=status.HTTP_200_OK)


# ============================================================================
# BROADCASTS VIEWSET
# ============================================================================

class BroadcastViewSet(viewsets.ModelViewSet):
    """Broadcasts uchun API."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'target_type']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Broadcast.objects.prefetch_related('recipients')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BroadcastDetailSerializer
        elif self.action == 'create':
            return BroadcastCreateSerializer
        elif self.action == 'launch':
            return BroadcastSendSerializer
        return BroadcastListSerializer

    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        """Broadcastni yuborish."""
        broadcast = self.get_object()

        if broadcast.status != Broadcast.Status.DRAFT:
            return Response(
                {"error": f"Cannot launch broadcast with status {broadcast.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        broadcast.status = Broadcast.Status.IN_PROGRESS
        broadcast.sent_at = timezone.now()
        broadcast.save(update_fields=['status', 'sent_at', 'updated_at'])

        serializer = BroadcastDetailSerializer(broadcast)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def recipients(self, request, pk=None):
        """Broadcast qabul qiluvchilar ro'yxati."""
        broadcast = self.get_object()
        recipients = broadcast.recipients.all()
        serializer = BroadcastRecipientSerializer(recipients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# DASHBOARD & STATS
# ============================================================================

class DashboardStatsView(APIView):
    """Dashboard statistikasi."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        active_count = (
            Subscription.objects.filter(
                status=Subscription.Status.ACTIVE,
                end_date__gt=now
            )
            .values("user")
            .distinct()
            .count()
        )

        monthly_revenue = (
            Transaction.objects.filter(
                status=Transaction.Status.PAID,
                paid_at__gte=month_start
            ).aggregate(total=Sum("amount"))["total"] or 0
        ) // 100

        today_revenue = (
            Transaction.objects.filter(
                status=Transaction.Status.PAID,
                paid_at__gte=today_start
            ).aggregate(total=Sum("amount"))["total"] or 0
        ) // 100

        expiring_7d = Subscription.objects.filter(
            status=Subscription.Status.ACTIVE,
            end_date__gt=now,
            end_date__lte=now + timedelta(days=7),
        ).count()

        stale_pending = Transaction.objects.filter(
            status=Transaction.Status.PENDING,
            created_at__lte=now - timedelta(minutes=30),
        ).count()

        data = {
            "active_subscribers": active_count,
            "monthly_revenue_uzs": monthly_revenue,
            "today_revenue_uzs": today_revenue,
            "expiring_7d": expiring_7d,
            "stale_pending": stale_pending,
            "total_users": TelegramUser.objects.count(),
            "total_channels": Channel.objects.count(),
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BroadcastStatusView(APIView):
    """Real-time broadcast progress."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        broadcast = get_object_or_404(Broadcast, pk=pk)

        progress_percent = 0
        if broadcast.total_count > 0:
            progress_percent = int((broadcast.sent_count / broadcast.total_count) * 100)

        data = {
            "status": broadcast.status,
            "total_count": broadcast.total_count,
            "sent_count": broadcast.sent_count,
            "failed_count": broadcast.failed_count,
            "progress_percent": progress_percent,
        }

        serializer = BroadcastStatusSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# PAYMENT SETTINGS
# ============================================================================

class PaymentSettingsView(APIView):
    """To'lov sozlamalari."""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        settings = PaymentSettings.load()
        serializer = PaymentSettingsSerializer(settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        settings = PaymentSettings.load()
        serializer = PaymentSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
