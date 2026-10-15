"""Fail-closed OIDC access-token verification boundary.

No authentication provider is configured by default. This module only validates
third-party issued access tokens; it does not authenticate passwords or create
sessions. Browser session architecture remains an explicit design decision.
"""
import os
from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import urlparse

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Identity:
    subject: str


@lru_cache(maxsize=8)
def _jwks_client(url: str) -> PyJWKClient:
    # Cache signing keys using PyJWT's key cache; refresh after rotation.
    return PyJWKClient(url, cache_keys=True, lifespan=300, timeout=5)


def _settings() -> tuple[str, str, str]:
    issuer = os.getenv("INFORMED_OIDC_ISSUER", "").rstrip("/")
    audience = os.getenv("INFORMED_OIDC_AUDIENCE", "")
    jwks_url = os.getenv("INFORMED_OIDC_JWKS_URL", "")
    if not all((issuer, audience, jwks_url)):
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    # These are operator-controlled values, never supplied by the token/client.
    for url in (issuer, jwks_url):
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise HTTPException(status_code=503, detail="Invalid authentication configuration")
    return issuer, audience, jwks_url


def require_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Identity:
    issuer, audience, jwks_url = _settings()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Bearer access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(credentials.credentials)
        claims = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            leeway=30,
        )
        subject = claims["sub"]
        if not isinstance(subject, str) or not subject.strip():
            raise InvalidTokenError("Missing subject")
        return Identity(subject=subject)
    except (InvalidTokenError, PyJWKClientError, ValueError, TimeoutError):
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
