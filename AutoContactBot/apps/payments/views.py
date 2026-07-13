"""
Payme Webhook View — JSON-RPC endpoint.
Handles: CheckPerformTransaction, CreateTransaction,
         PerformTransaction, CancelTransaction, CheckTransaction
"""
import logging
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.payments.models import Transaction
from apps.payments.payme import (
    PaymeWebhookValidator,
    TRANSACTION_STATE_CREATED,
    TRANSACTION_STATE_COMPLETED,
    TRANSACTION_STATE_CANCELLED_BEFORE,
    TRANSACTION_STATE_CANCELLED_AFTER,
    PaymeInvoiceGenerator,
)

logger = logging.getLogger(__name__)
validator = PaymeWebhookValidator()


@method_decorator(csrf_exempt, name="dispatch")
class PaymeWebhookView(View):
    """Payme Merchant API JSON-RPC endpoint."""

    def post(self, request, *args, **kwargs):
        import json

        # IP tekshirish
        remote_ip = self._get_client_ip(request)
        if not validator.validate_ip(remote_ip):
            logger.warning("Payme webhook rejected: invalid IP %s", remote_ip)
            return JsonResponse(
                validator.make_error_response(-32504, "Insufficient privilege"),
                status=200,
            )

        # Auth tekshirish
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not validator.validate_auth(auth_header):
            logger.warning("Payme webhook rejected: invalid auth from IP %s", remote_ip)
            return JsonResponse(
                validator.make_error_response(-32504, "Insufficient privilege"),
                status=200,
            )

        # JSON parse
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                validator.make_error_response(-32700, "Parse error"),
                status=200,
            )

        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")

        logger.info("Payme webhook method=%s params=%s", method, params)

        dispatch = {
            "CheckPerformTransaction": self._check_perform_transaction,
            "CreateTransaction": self._create_transaction,
            "PerformTransaction": self._perform_transaction,
            "CancelTransaction": self._cancel_transaction,
            "CheckTransaction": self._check_transaction,
        }

        handler = dispatch.get(method)
        if not handler:
            return JsonResponse(
                validator.make_error_response(-32601, "Method not found", request_id),
                status=200,
            )

        return JsonResponse(handler(params, request_id), status=200)

    # ------------------------------------------------------------------
    # CheckPerformTransaction
    # ------------------------------------------------------------------
    def _check_perform_transaction(self, params: dict, request_id) -> dict:
        order_id = params.get("account", {}).get("order_id")
        amount = params.get("amount")

        try:
            import uuid as _uuid
            order_uuid = _uuid.UUID(str(order_id))
            transaction = Transaction.objects.get(id=order_uuid, status=Transaction.Status.PENDING)
        except (Transaction.DoesNotExist, ValueError, AttributeError):
            return validator.make_error_response(-32100, "Order not found", request_id)

        if transaction.amount != amount:
            return validator.make_error_response(-32102, "Wrong amount", request_id)

        return validator.make_success_response({"allow": True}, request_id)

    # ------------------------------------------------------------------
    # CreateTransaction
    # ------------------------------------------------------------------
    def _create_transaction(self, params: dict, request_id) -> dict:
        order_id = params.get("account", {}).get("order_id")
        payme_transaction_id = params.get("id")
        amount = params.get("amount")
        create_time = params.get("time", PaymeInvoiceGenerator.current_time_ms())

        try:
            import uuid as _uuid
            order_uuid = _uuid.UUID(str(order_id))
            transaction = Transaction.objects.get(id=order_uuid)
        except (Transaction.DoesNotExist, ValueError, AttributeError):
            return validator.make_error_response(-32100, "Order not found", request_id)

        if transaction.amount != amount:
            return validator.make_error_response(-32102, "Wrong amount", request_id)

        # Agar allaqachon payme_transaction_id bor bo'lsa — duplicate check
        if transaction.payme_transaction_id and transaction.payme_transaction_id != payme_transaction_id:
            return validator.make_error_response(-32300, "Transaction not permitted", request_id)

        if transaction.status == Transaction.Status.CANCELLED:
            return validator.make_error_response(
                -32300, "Transaction cancelled", request_id
            )

        # Yangi Payme transaction ID ni saqlash
        transaction.payme_transaction_id = payme_transaction_id
        transaction.payme_state = TRANSACTION_STATE_CREATED
        transaction.payme_create_time = create_time
        transaction.save(update_fields=["payme_transaction_id", "payme_state", "payme_create_time"])

        return validator.make_success_response(
            {
                "create_time": create_time,
                "transaction": str(transaction.id),
                "state": TRANSACTION_STATE_CREATED,
            },
            request_id,
        )

    # ------------------------------------------------------------------
    # PerformTransaction
    # ------------------------------------------------------------------
    def _perform_transaction(self, params: dict, request_id) -> dict:
        payme_transaction_id = params.get("id")
        perform_time = PaymeInvoiceGenerator.current_time_ms()

        try:
            transaction = Transaction.objects.select_related(
                "user", "channel", "tariff"
            ).get(payme_transaction_id=payme_transaction_id)
        except Transaction.DoesNotExist:
            return validator.make_error_response(-32100, "Transaction not found", request_id)

        if transaction.status == Transaction.Status.PAID:
            # Idempotent — already performed
            return validator.make_success_response(
                {
                    "transaction": str(transaction.id),
                    "perform_time": transaction.payme_perform_time or perform_time,
                    "state": TRANSACTION_STATE_COMPLETED,
                },
                request_id,
            )

        if transaction.status == Transaction.Status.CANCELLED:
            return validator.make_error_response(
                -32300, "Transaction cancelled", request_id
            )

        # Mark as paid
        transaction.status = Transaction.Status.PAID
        transaction.payme_state = TRANSACTION_STATE_COMPLETED
        transaction.payme_perform_time = perform_time
        transaction.paid_at = timezone.now()
        transaction.save(update_fields=[
            "status", "payme_state", "payme_perform_time", "paid_at"
        ])

        # Obunani faollashtirish (background task)
        from apps.notifications.tasks import activate_subscription_task
        activate_subscription_task.delay(str(transaction.id))

        logger.info("Transaction performed: %s", transaction.id)
        return validator.make_success_response(
            {
                "transaction": str(transaction.id),
                "perform_time": perform_time,
                "state": TRANSACTION_STATE_COMPLETED,
            },
            request_id,
        )

    # ------------------------------------------------------------------
    # CancelTransaction
    # ------------------------------------------------------------------
    def _cancel_transaction(self, params: dict, request_id) -> dict:
        payme_transaction_id = params.get("id")
        reason = params.get("reason", 0)
        cancel_time = PaymeInvoiceGenerator.current_time_ms()

        try:
            transaction = Transaction.objects.select_related("subscription").get(
                payme_transaction_id=payme_transaction_id
            )
        except Transaction.DoesNotExist:
            return validator.make_error_response(-32100, "Transaction not found", request_id)

        if transaction.status == Transaction.Status.PAID:
            # Bajarilgan to'lovni bekor qilib bo'lmaydi (lekin qoidaga ko'ra state qaytaramiz)
            state = TRANSACTION_STATE_CANCELLED_AFTER
            transaction.payme_state = state
        else:
            state = TRANSACTION_STATE_CANCELLED_BEFORE
            transaction.payme_state = state

        transaction.status = Transaction.Status.CANCELLED
        transaction.cancel_reason = reason
        transaction.payme_cancel_time = cancel_time
        transaction.cancelled_at = timezone.now()
        transaction.save(update_fields=[
            "status", "payme_state", "cancel_reason", "payme_cancel_time", "cancelled_at"
        ])

        # Faol obunani ham bekor qilish
        if transaction.subscription and transaction.subscription.status == "active":
            transaction.subscription.status = "cancelled"
            transaction.subscription.save(update_fields=["status", "updated_at"])

        logger.info("Transaction cancelled: %s reason=%s", transaction.id, reason)
        return validator.make_success_response(
            {
                "transaction": str(transaction.id),
                "cancel_time": cancel_time,
                "state": state,
            },
            request_id,
        )

    # ------------------------------------------------------------------
    # CheckTransaction
    # ------------------------------------------------------------------
    def _check_transaction(self, params: dict, request_id) -> dict:
        payme_transaction_id = params.get("id")

        try:
            transaction = Transaction.objects.get(payme_transaction_id=payme_transaction_id)
        except Transaction.DoesNotExist:
            return validator.make_error_response(-32100, "Transaction not found", request_id)

        return validator.make_success_response(
            {
                "create_time": transaction.payme_create_time or 0,
                "perform_time": transaction.payme_perform_time or 0,
                "cancel_time": transaction.payme_cancel_time or 0,
                "transaction": str(transaction.id),
                "state": transaction.payme_state or TRANSACTION_STATE_CREATED,
                "reason": transaction.cancel_reason,
            },
            request_id,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _get_client_ip(request) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
