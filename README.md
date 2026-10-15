# Informed

Nonpartisan, interest-aligned voter intelligence with traceable legislative evidence.

## Status
Early foundation scaffold. **Not production-ready**: authentication, ZeroDB integration, consent, encryption and private profile storage have not been implemented. `POST /v1/profiles` deliberately returns HTTP 501.

## Architecture
- `frontend/` — React + TypeScript + Vite; TanStack Query dependency
- `backend/` — Python FastAPI + Pydantic
- `PRD.MD`, `datamodel.md`, `backlog.md` — design and acceptance criteria
- `AGENTS.md` — repository instructions for coding agents

## Run API
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest
```
On Windows use `.venv\\Scripts\\activate` instead of `source`.

## Run web app
```bash
cd frontend
npm install
npm run dev
npm run build
```

## Security decisions required before user accounts
1. Select an OIDC identity provider and server-side session strategy; document CSRF, logout, expiry and refresh handling.
2. Implement authorization and cross-user isolation on all private endpoints.
3. Design KMS-backed per-user encryption keys, key rotation and deletion.
4. Specify explicit consent, anonymous in-browser mode and retention.
5. Implement server-side ZeroDB MCP access using secrets management, with no credentials in client bundles.
6. Add security/neutrality tests and CI before enabling profile persistence.

Never enter real voter preferences into this scaffold.
