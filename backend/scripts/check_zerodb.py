"""Verify project-scoped ZeroDB access without writing data or printing secrets.

Run: python scripts/check_zerodb.py
Reads backend/.env.local or repository-root .env.local (without third-party dotenv).
"""
import os
import sys
from pathlib import Path

import httpx


def load_local_env() -> None:
    root = Path(__file__).resolve().parents[2]
    candidates = (root / ".env.local", root / "backend" / ".env.local")
    for path in candidates:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, value = stripped.split("=", 1)
            name = name.strip()
            if name in {"ZERODB_API_URL", "ZERODB_PROJECT_ID", "ZERODB_API_KEY"}:
                os.environ.setdefault(name, value.strip().strip('"').strip("'"))


def check() -> int:
    load_local_env()
    url = os.environ.get("ZERODB_API_URL", "https://api.ainative.studio").rstrip("/")
    project_id = os.environ.get("ZERODB_PROJECT_ID", "")
    key = os.environ.get("ZERODB_API_KEY", "")
    if not project_id or not key:
        print("Missing ZERODB_PROJECT_ID or ZERODB_API_KEY in local environment.")
        return 2
    if url != "https://api.ainative.studio":
        print("Nonstandard API URL; refusing to transmit credentials.")
        return 2
    endpoint = f"{url}/api/v1/projects/{project_id}/database/tables"
    try:
        with httpx.Client(timeout=10.0, follow_redirects=False) as client:
            response = client.get(endpoint, headers={"X-API-Key": key})
    except httpx.RequestError:
        print("Connection failed: network or TLS error.")
        return 1
    if response.status_code == 200:
        print("ZeroDB connection verified: project tables endpoint accessible.")
        return 0
    if response.status_code in (401, 403):
        print("Authentication failed: verify the API key and its project permissions.")
    elif response.status_code == 404:
        print("Project unavailable: verify the project ID and key ownership.")
    else:
        print(f"ZeroDB returned HTTP {response.status_code}; no credentials displayed.")
    return 1


if __name__ == "__main__":
    sys.exit(check())
