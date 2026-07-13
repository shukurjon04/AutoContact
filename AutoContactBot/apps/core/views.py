"""Health check endpoint."""
import logging
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Returns HTTP 200 if all dependencies are healthy, 503 otherwise.
    Checked: PostgreSQL, Redis
    """
    checks = {}
    all_healthy = True

    # PostgreSQL
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        all_healthy = False
        logger.error("Health check: database error: %s", e)

    # Redis
    try:
        cache.set("health_check", "ok", timeout=5)
        result = cache.get("health_check")
        checks["redis"] = "ok" if result == "ok" else "error: unexpected value"
        if result != "ok":
            all_healthy = False
    except Exception as e:
        checks["redis"] = f"error: {e}"
        all_healthy = False
        logger.error("Health check: redis error: %s", e)

    status = 200 if all_healthy else 503
    return JsonResponse({"status": "healthy" if all_healthy else "degraded", "checks": checks}, status=status)
