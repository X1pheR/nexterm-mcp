from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import Settings


class NextermError(RuntimeError):
    pass


SENSITIVE_KEYS = {
    "password",
    "passphrase",
    "sshkey",
    "ssh_key",
    "privatekey",
    "private_key",
    "token",
    "accesstoken",
    "access_token",
    "refreshtoken",
    "refresh_token",
    "apikey",
    "api_key",
    "authorization",
    "cookie",
    "secret",
    "credentials",
}


def _normalized_key(key: Any) -> str:
    return str(key).replace("-", "_").lower()


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: sanitize(item)
            for key, item in value.items()
            if _normalized_key(key) not in SENSITIVE_KEYS
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


class NextermClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.settings.base_url}{path}"
        if query:
            filtered = {key: value for key, value in query.items() if value is not None}
            if filtered:
                url = f"{url}?{urlencode(filtered, doseq=True)}"
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.settings.read_api_key()}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "nexterm-mcp/0.2.0",
            },
        )
        try:
            with urlopen(request, timeout=self.settings.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as error:
            raise NextermError(f"Nexterm API returned HTTP {error.code} for {method} {path}") from None
        except URLError as error:
            reason = getattr(error, "reason", "connection failed")
            raise NextermError(f"Nexterm API request failed for {method} {path}: {reason}") from None
        except TimeoutError:
            raise NextermError(f"Nexterm API request timed out for {method} {path}") from None

        if not raw:
            return None
        try:
            return sanitize(json.loads(raw.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise NextermError(f"Nexterm API returned a non-JSON response for {method} {path}") from None

    def list_entries(self) -> Any:
        return self.request("GET", "/api/entries/list")

    def get_entry(self, entry_id: int) -> Any:
        return self.request("GET", f"/api/entries/{entry_id}")
