"""Authentication boundary tests. Never use real user tokens."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.auth import _jwks_client
from app.main import app

client = TestClient(app)
ISSUER = "https://issuer.example.test"
AUDIENCE = "informed-api"
JWKS = "https://issuer.example.test/.well-known/jwks.json"


@pytest.fixture(autouse=True)
def configure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("INFORMED_OIDC_ISSUER", ISSUER)
    monkeypatch.setenv("INFORMED_OIDC_AUDIENCE", AUDIENCE)
    monkeypatch.setenv("INFORMED_OIDC_JWKS_URL", JWKS)
    yield
    _jwks_client.cache_clear()


def test_missing_token_is_rejected():
    response = client.get("/v1/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_malformed_token_is_rejected():
    response = client.get("/v1/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401


def test_unconfigured_provider_fails_closed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("INFORMED_OIDC_JWKS_URL")
    response = client.get("/v1/me", headers={"Authorization": "Bearer anything"})
    assert response.status_code == 503


def test_expired_or_wrong_audience_is_rejected():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    base = {"sub": "test-user", "iss": ISSUER, "aud": AUDIENCE, "iat": now}
    with patch("app.auth._jwks_client", return_value=SimpleNamespace(
        get_signing_key_from_jwt=lambda _: SimpleNamespace(key=key.public_key())
    )):
        for extra in ({"exp": now - timedelta(minutes=5)},
                      {"exp": now + timedelta(minutes=5), "aud": "wrong-api"}):
            token = jwt.encode({**base, **extra}, key, algorithm="RS256")
            response = client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 401


def test_valid_provider_issued_token():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    token = jwt.encode({
        "sub": "synthetic-test-user", "iss": ISSUER, "aud": AUDIENCE,
        "iat": now, "exp": now + timedelta(minutes=5),
    }, key, algorithm="RS256")
    with patch("app.auth._jwks_client", return_value=SimpleNamespace(
        get_signing_key_from_jwt=lambda _: SimpleNamespace(key=key.public_key())
    )):
        response = client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"subject": "synthetic-test-user"}
    assert response.headers["cache-control"] == "no-store"
