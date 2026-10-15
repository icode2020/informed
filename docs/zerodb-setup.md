# Informed local ZeroDB connectivity

Store credentials **only** in `backend/.env.local` or repository-root `.env.local`;
both paths are ignored by the repository's `.gitignore` after PR #113 merges.
Never commit a populated credentials file or copy API keys into GitHub issues.

Example (placeholders only):

```dotenv
ZERODB_API_URL=https://api.ainative.studio
ZERODB_PROJECT_ID=<your-project-uuid>
ZERODB_API_KEY=<your-private-key>
```

## Connection check (read-only)

From `backend/` run:

```bash
python -m pip install -e ".[dev]"
python scripts/check_zerodb.py
```

The command calls `GET /api/v1/projects/{project_id}/database/tables`
with `X-API-Key` and prints only a result status, never the key.
This is a **read-only connectivity check**, not data model bootstrap or
ZeroDB MCP integration. If the server responds 401/403, check the key; 404
suggests a missing or inaccessible project.

Only use a development project until consent, authorization and
encryption are implemented. Do not upload voter profiles.
