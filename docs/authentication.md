# Authentication and privacy boundary (milestone 2)

## Status
**Implemented:** optional OIDC JWT *resource-server validation* for `GET /v1/me`.
**Not implemented:** sign-in UI, browser sessions, refresh-token handling, logout,
OIDC provider provisioning, ZeroDB connection, consent recording, KMS, encrypted
profile storage, access-control policies or production deployment.

Authentication is disabled by default. Missing/invalid configuration causes the
protected endpoint to respond HTTP 503; missing, expired or invalid access tokens
are rejected. The existing profile endpoint continues to return HTTP 501 and
**does not persist any voter preferences**.

## Operator configuration (server only)
- `INFORMED_OIDC_ISSUER` — exact HTTPS issuer from provider discovery metadata.
- `INFORMED_OIDC_AUDIENCE` — API audience identifier assigned by the provider.
- `INFORMED_OIDC_JWKS_URL` — provider's trusted HTTPS signing-key endpoint.

Never use ID tokens as API access tokens. Configure your provider to issue JWT
access tokens for the Informed API audience signed with RS256. Backend validates
signature, algorithm, issuer, audience, subject and required timestamps. JWKS
is obtained only from an operator-configured endpoint, never from token headers.

Do not put client secrets or provider administrative tokens in the frontend.
API signing keys remain with the identity provider.

## Request flow (API clients, not yet browser login)
1. Approved identity provider issues an access token for `informed-api`.
2. API client calls `GET /v1/me` with `Authorization: Bearer <access-token>`.
3. FastAPI verifies the RS256 signature against trusted JWKS and checks claims.
4. A validated opaque user subject is returned with `Cache-Control: no-store`.

## Production design decisions (not yet approved)
- Select an OIDC provider and configure its API audience and issuer.
- Prefer a backend-for-frontend with authorization-code + PKCE, secure HttpOnly
  cookies, session rotation, CSRF protection and server-side logout.
- Introduce explicit consent before saving special-category political interests.
- Define KMS-backed per-user data keys and authenticated AES-256-GCM ciphertext;
  use HMAC-derived row IDs, never plaintext user identifiers in ZeroDB.
- Enforce user ownership at backend repository boundaries. Never accept profile IDs
  as authority; validate cross-user denial tests.
- Add anonymous in-browser mode without server-side interests or AI memory.
- Threat-model logs, error reporting, retention, abuse protection and third parties.

This implementation is a boundary, not a complete authentication system.
