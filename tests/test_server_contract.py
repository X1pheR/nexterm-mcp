from __future__ import annotations

import asyncio

from nexterm_mcp.server import _create_payload, _update_payload, list_tools
from nexterm_mcp.models import CreateEntryInput


def test_public_tool_surface_is_bounded() -> None:
    tools = asyncio.run(list_tools())
    names = {tool.name for tool in tools}
    assert names == {
        "nexterm_status",
        "nexterm_list_entries",
        "nexterm_get_entry",
        "nexterm_list_identities",
        "nexterm_list_folders",
        "nexterm_create_entry",
        "nexterm_update_entry",
        "nexterm_delete_entry",
    }
    assert not any("request" in name or "http" in name or "api_key" in name for name in names)
    delete_tool = next(tool for tool in tools if tool.name == "nexterm_delete_entry")
    assert delete_tool.annotations.destructiveHint is True


def test_create_payload_matches_nexterm_entry_shape() -> None:
    args = CreateEntryInput(name="oci-vps", ip="203.0.113.10", port=22, identity_ids=[7], monitoring_enabled=True)
    assert _create_payload(args) == {
        "name": "oci-vps",
        "type": "server",
        "identities": [7],
        "config": {"protocol": "ssh", "ip": "203.0.113.10", "port": 22, "monitoringEnabled": True},
    }


def test_update_payload_preserves_existing_config_fields() -> None:
    from nexterm_mcp.models import UpdateEntryInput

    args = UpdateEntryInput(entry_id=4, port=2222)
    existing = {"config": {"protocol": "ssh", "ip": "203.0.113.10", "port": 22, "keyboardLayout": "en-us"}}
    assert _update_payload(args, existing) == {
        "config": {"protocol": "ssh", "ip": "203.0.113.10", "port": 2222, "keyboardLayout": "en-us"}
    }
