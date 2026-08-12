from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


class ConfigurationError(RuntimeError):
    pass


def _private_file(path_text: str) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        raise ConfigurationError("NEXTERM_API_KEY_FILE must be an absolute path")
    try:
        info = path.lstat()
    except FileNotFoundError as error:
        raise ConfigurationError(f"API key file does not exist: {path}") from error
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ConfigurationError("API key file must be a regular non-symlink file")
    if info.st_mode & 0o077:
        raise ConfigurationError("API key file must not grant group or other permissions")
    return path


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be true or false")


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key_file: Path
    timeout_seconds: float = 15.0
    mutations_enabled: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        base_url = os.environ.get("NEXTERM_BASE_URL", "").strip().rstrip("/")
        if not base_url:
            raise ConfigurationError("NEXTERM_BASE_URL is required")
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
            raise ConfigurationError("NEXTERM_BASE_URL must be an http(s) origin or path without query/fragment")

        key_file_text = os.environ.get("NEXTERM_API_KEY_FILE", "").strip()
        if not key_file_text:
            raise ConfigurationError("NEXTERM_API_KEY_FILE is required")
        key_file = _private_file(key_file_text)

        try:
            timeout = float(os.environ.get("NEXTERM_TIMEOUT_SECONDS", "15"))
        except ValueError as error:
            raise ConfigurationError("NEXTERM_TIMEOUT_SECONDS must be numeric") from error
        if timeout <= 0 or timeout > 120:
            raise ConfigurationError("NEXTERM_TIMEOUT_SECONDS must be > 0 and <= 120")

        return cls(
            base_url=base_url,
            api_key_file=key_file,
            timeout_seconds=timeout,
            mutations_enabled=_bool("NEXTERM_MUTATIONS_ENABLED", False),
        )

    def read_api_key(self) -> str:
        token = self.api_key_file.read_text(encoding="utf-8").strip()
        if not token:
            raise ConfigurationError("API key file is empty")
        return token
