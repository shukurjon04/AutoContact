"""
Payme Webhook integration tests.
"""
import base64
import json
import uuid
import pytest
from django.test import Client
from django.conf import settings


def _make_auth_header(secret_key: str) -> str:
    encoded = base64.b64encode(f"Paycom:{secret_key}".encode()).decode()
    return f"Basic {encoded}"


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def auth_headers():
    secret = settings.PAYME_TEST_SECRET_KEY or settings.PAYME_SECRET_KEY
    return {
        "HTTP_AUTHORIZATION": _make_auth_header(secret),
        "REMOTE_ADDR": "185.8.212.184",  # Payme test IP (allowed in DEBUG mode)
        "content_type": "application/json",
    }


@pytest.mark.django_db
def test_payme_webhook_invalid_auth(client):
    payload = {
        "id": 1,
        "method": "CheckPerformTransaction",
        "params": {"account": {"order_id": str(uuid.uuid4())}, "amount": 10000},
    }
    resp = client.post(
        "/payme/webhook/",
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_AUTHORIZATION="Basic invalid",
        REMOTE_ADDR="185.8.212.184",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == -32504


@pytest.mark.django_db
def test_check_perform_transaction_not_found(client, auth_headers):
    payload = {
        "id": 1,
        "method": "CheckPerformTransaction",
        "params": {
            "account": {"order_id": str(uuid.uuid4())},
            "amount": 5000000,
        },
    }
    resp = client.post(
        "/payme/webhook/",
        data=json.dumps(payload),
        **auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    # Order doesn't exist → -32100
    assert data.get("error", {}).get("code") == -32100


@pytest.mark.django_db
def test_check_transaction_not_found(client, auth_headers):
    payload = {
        "id": 2,
        "method": "CheckTransaction",
        "params": {"id": "nonexistent_payme_id"},
    }
    resp = client.post(
        "/payme/webhook/",
        data=json.dumps(payload),
        **auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("error", {}).get("code") == -32100
