from __future__ import annotations

from pathlib import Path

import pytest

from nexterm_mcp.config import ConfigurationError, Settings


def test_settings_require_private_key_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    key = tmp_path / "key"
    key.write_text("nxt_test", encoding="utf-8")
    key.chmod(0o644)
    monkeypatch.setenv("NEXTERM_BASE_URL", "https://nexterm.example")
    monkeypatch.setenv("NEXTERM_API_KEY_FILE", str(key))
    with pytest.raises(ConfigurationError, match="group or other"):
        Settings.from_env()


def test_mutations_default_off(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    key = tmp_path / "key"
    key.write_text("nxt_test", encoding="utf-8")
    key.chmod(0o600)
    monkeypatch.setenv("NEXTERM_BASE_URL", "https://nexterm.example/")
    monkeypatch.setenv("NEXTERM_API_KEY_FILE", str(key))
    monkeypatch.delenv("NEXTERM_MUTATIONS_ENABLED", raising=False)
    settings = Settings.from_env()
    assert settings.base_url == "https://nexterm.example"
    assert settings.mutations_enabled is False
