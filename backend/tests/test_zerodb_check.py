"""Purely local credential-loading and failure-mode tests."""
from pathlib import Path
from unittest.mock import patch

from scripts import check_zerodb


def test_missing_credentials_fail_closed(monkeypatch):
    monkeypatch.setattr(check_zerodb, "load_local_env", lambda: None)
    monkeypatch.delenv("ZERODB_PROJECT_ID", raising=False)
    monkeypatch.delenv("ZERODB_API_KEY", raising=False)
    assert check_zerodb.check() == 2


def test_success_never_prints_key(monkeypatch, capsys):
    monkeypatch.setattr(check_zerodb, "load_local_env", lambda: None)
    monkeypatch.setenv("ZERODB_PROJECT_ID", "test-project")
    monkeypatch.setenv("ZERODB_API_KEY", "synthetic-secret")
    monkeypatch.setenv("ZERODB_API_URL", "https://api.ainative.studio")
    class FakeClient:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): return None
        def get(self, url, headers):
            assert headers == {"X-API-Key": "synthetic-secret"}
            assert url.endswith("/api/v1/projects/test-project/database/tables")
            return type("Response", (), {"status_code": 200})()
    with patch.object(check_zerodb.httpx, "Client", FakeClient):
        assert check_zerodb.check() == 0
    assert "synthetic-secret" not in capsys.readouterr().out
