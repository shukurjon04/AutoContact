"""
Payme Merchant API integration.
JSON-RPC 2.0 over HTTP/HTTPS.
Docs: https://developer.payme.uz/documentation
"""
import base64
import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Payme JSON-RPC Error codes
# ---------------------------------------------------------------------------
PAYME_ERRORS = {
    -32700: "Parse error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    -32400: "System error",
    -32300: "Transaction not permitted",
    -32100: "Order not found",
    -32101: "Order already exists",
    -32102: "Wrong amount",
    -32300: "Transaction cancelled",
    -32301: "Cannot cancel transaction (already performed)",
    -32504: "Insufficient privilege",
}

TRANSACTION_STATE_CREATED = 1
TRANSACTION_STATE_COMPLETED = 2
TRANSACTION_STATE_CANCELLED_BEFORE = -1
TRANSACTION_STATE_CANCELLED_AFTER = -2


@dataclass
class PaymeResult:
    success: bool
    result: dict | None = None
    error: dict | None = None


class PaymeWebhookValidator:
    """Payme webhook so'rovlarini tekshiradi."""

    def __init__(self):
        self.secret_key = (
            settings.PAYME_TEST_SECRET_KEY
            if settings.PAYME_TEST_MODE
            else settings.PAYME_SECRET_KEY
        )
        self.allowed_ips: list[str] = settings.PAYME_ALLOWED_IPS

    def validate_ip(self, remote_ip: str) -> bool:
        """IP manzilini Payme ruxsat etilgan IP ro'yxati bilan tekshiradi."""
        if settings.DEBUG:
            return True  # dev muhitida IP tekshirishni o'tkazib yuboring
        return remote_ip in self.allowed_ips

    def validate_auth(self, auth_header: str) -> bool:
        """Authorization: Basic <base64(merchant_id:secret_key)> tekshiradi."""
        try:
            if not auth_header.startswith("Basic "):
                return False
            encoded = auth_header.split(" ", 1)[1]
            decoded = base64.b64decode(encoded).decode("utf-8")
            _, provided_key = decoded.split(":", 1)
            return provided_key == self.secret_key
        except Exception:
            return False

    @staticmethod
    def make_error_response(code: int, message: str, request_id: Any = None) -> dict:
        return {
            "id": request_id,
            "error": {
                "code": code,
                "message": {"ru": message, "uz": message, "en": message},
                "data": None,
            },
        }

    @staticmethod
    def make_success_response(result: dict, request_id: Any = None) -> dict:
        return {
            "id": request_id,
            "result": result,
        }


class PaymeInvoiceGenerator:
    """Payme to'lov havolasini yaratadi."""

    CHECKOUT_URL = "https://checkout.paycom.uz"
    TEST_CHECKOUT_URL = "https://test.paycom.uz"

    def __init__(self):
        self.merchant_id = settings.PAYME_MERCHANT_ID
        self.test_mode = settings.PAYME_TEST_MODE

    def generate_payment_url(self, order_id: str, amount_tiyin: int, description: str = "") -> str:
        """
        Payme checkout havolasini yaratadi.
        amount_tiyin: tiyin da (1 UZS = 100 tiyin)
        """
        base_url = self.TEST_CHECKOUT_URL if self.test_mode else self.CHECKOUT_URL
        params = f"m={self.merchant_id};ac.order_id={order_id};a={amount_tiyin};l=uz"
        encoded = base64.b64encode(params.encode("utf-8")).decode("utf-8")
        url = f"{base_url}/{encoded}"
        logger.debug("Generated Payme URL for order %s: %s", order_id, url)
        return url

    @staticmethod
    def current_time_ms() -> int:
        return int(time.time() * 1000)
