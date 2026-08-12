from nexterm_mcp.client import sanitize


def test_sanitize_removes_credential_fields_recursively() -> None:
    value = {
        "id": 3,
        "password": "hidden",
        "nested": {"sshKey": "hidden", "username": "safe"},
        "items": [{"passphrase": "hidden", "name": "safe"}],
    }
    assert sanitize(value) == {"id": 3, "nested": {"username": "safe"}, "items": [{"name": "safe"}]}
