"""REST API URL configuration — barcha resource endpoints."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.api.views import (
    ProfileView,
    TelegramUserViewSet,
    ChannelViewSet,
    TariffViewSet,
    SubscriptionViewSet,
    TransactionViewSet,
    BroadcastViewSet,
    DashboardStatsView,
    BroadcastStatusView,
    PaymentSettingsView,
)

app_name = "api"

# Router registration
router = DefaultRouter()
router.register(r'users', TelegramUserViewSet, basename='user')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'tariffs', TariffViewSet, basename='tariff')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'broadcasts', BroadcastViewSet, basename='broadcast')

urlpatterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', ProfileView.as_view(), name='profile'),

    # Dashboard & Statistics
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('broadcasts/<int:pk>/status/', BroadcastStatusView.as_view(), name='broadcast_status'),

    # Payment Settings
    path('payment-settings/', PaymentSettingsView.as_view(), name='payment_settings'),

    # Router URLs (CRUD operations)
    path('', include(router.urls)),
]
