from __future__ import annotations

import json
from pathlib import Path

import pytest

from nexterm_mcp.client import NextermClient, sanitize
from nexterm_mcp.config import Settings


def test_sanitize_removes_credential_fields_recursively() -> None:
    value = {
        "id": 3,
        "password": "hidden",
        "apiKey": "hidden",
        "accessToken": "hidden",
        "nested": {"sshKey": "hidden", "username": "safe"},
        "items": [{"passphrase": "hidden", "name": "safe"}],
    }
    assert sanitize(value) == {"id": 3, "nested": {"username": "safe"}, "items": [{"name": "safe"}]}


def test_request_encodes_query_and_never_places_api_key_in_url(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    key = tmp_path / "key"
    key.write_text("nxt_private", encoding="utf-8")
    key.chmod(0o600)
    settings = Settings(base_url="https://nexterm.example", api_key_file=key)
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return json.dumps({"password": "hidden", "items": [1, 2]}).encode()

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.get_header("Authorization")
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("nexterm_mcp.client.urlopen", fake_urlopen)
    result = NextermClient(settings).request(
        "GET",
        "/api/audit/logs",
        query={"organizationId": "personal", "limit": 50, "unused": None},
    )

    assert captured["url"] == "https://nexterm.example/api/audit/logs?organizationId=personal&limit=50"
    assert captured["authorization"] == "Bearer nxt_private"
    assert "nxt_private" not in captured["url"]
    assert result == {"items": [1, 2]}
