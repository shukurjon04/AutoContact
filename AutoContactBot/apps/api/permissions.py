"""Custom permissions for REST API."""
from rest_framework.permissions import BasePermission, IsAdminUser as DRFIsAdminUser


class IsAdmin(DRFIsAdminUser):
    """Admin faqat uchun."""
    message = "Admin ruxsatnomasi kerak."


class IsAdminOrReadOnly(BasePermission):
    """Admin o'zgartira oladi, boshqalar o'qiy oladi."""
    message = "Admin ruxsatnomasi kerak."

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff


class CanApproveTransaction(BasePermission):
    """Tranzaksiyani tasdiqlash uchun."""
    message = "Tranzaksiyani tasdiqlash ruxsatnomasi kerak."

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class CanManageBroadcasts(BasePermission):
    """Broadcastlar bilan ishlash uchun."""
    message = "Broadcast bilan ishlash ruxsatnomasi kerak."

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
