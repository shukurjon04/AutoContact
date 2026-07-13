"""
Bot webhook URL — Nginx proxies /bot/webhook/ → bot container (aiohttp :8080).
Django does NOT handle this path directly.
This empty urlpatterns prevents import errors.
"""
from django.urls import path

urlpatterns: list = []
