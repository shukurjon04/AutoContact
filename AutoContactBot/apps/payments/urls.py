from django.urls import path
from .views import PaymeWebhookView

app_name = "payments"

urlpatterns = [
    path("webhook/", PaymeWebhookView.as_view(), name="payme-webhook"),
]
