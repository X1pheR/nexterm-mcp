from __future__ import annotations

import asyncio

from nexterm_mcp.models import CreateEntryInput, SetActiveThemeInput, UpdateEntryInput
from nexterm_mcp.operations import OPERATION_BY_NAME, create_entry_payload, update_entry_payload
from nexterm_mcp.server import list_tools


def test_public_tool_surface_is_broad_but_has_no_raw_or_secret_management_tools() -> None:
    tools = asyncio.run(list_tools())
    names = {tool.name for tool in tools}

    assert len(tools) == 89
    assert len(names) == len(tools)
    assert {
        "nexterm_status",
        "nexterm_list_entries",
        "nexterm_create_entry",
        "nexterm_create_folder",
        "nexterm_create_tag",
        "nexterm_list_organizations",
        "nexterm_create_script",
        "nexterm_create_snippet",
        "nexterm_create_theme",
        "nexterm_create_source",
        "nexterm_get_monitoring",
        "nexterm_get_audit_logs",
        "nexterm_create_backup",
        "nexterm_get_integration",
        "nexterm_list_engines",
    } <= names

    forbidden_fragments = {
        "api_request",
        "http_request",
        "api_key",
        "create_identity",
        "update_identity",
        "create_integration",
        "update_integration",
        "create_backup_provider",
        "update_backup_provider",
        "regenerate_engine",
        "create_engine",
    }
    assert not any(fragment in name for name in names for fragment in forbidden_fragments)

    destructive = {tool.name for tool in tools if tool.annotations and tool.annotations.destructiveHint}
    assert {
        "nexterm_delete_entry",
        "nexterm_delete_folder",
        "nexterm_delete_organization",
        "nexterm_delete_source",
        "nexterm_restore_backup",
        "nexterm_stop_integration_entry",
        "nexterm_shutdown_integration_entry",
    } <= destructive

    validate_source = next(tool for tool in tools if tool.name == "nexterm_validate_source")
    assert validate_source.annotations.readOnlyHint is True


def test_v010_core_tool_names_are_preserved() -> None:
    names = {tool.name for tool in asyncio.run(list_tools())}
    assert {
        "nexterm_status",
        "nexterm_list_entries",
        "nexterm_get_entry",
        "nexterm_list_identities",
        "nexterm_list_folders",
        "nexterm_create_entry",
        "nexterm_update_entry",
        "nexterm_delete_entry",
    } <= names


def test_create_payload_matches_nexterm_entry_shape() -> None:
    args = CreateEntryInput(
        name="oci-vps",
        ip="203.0.113.10",
        port=22,
        identity_ids=[7],
        monitoring_enabled=True,
        wake_on_lan_enabled=False,
    )
    assert create_entry_payload(args) == {
        "name": "oci-vps",
        "type": "server",
        "identities": [7],
        "config": {
            "protocol": "ssh",
            "ip": "203.0.113.10",
            "port": 22,
            "monitoringEnabled": True,
            "wakeOnLanEnabled": False,
        },
    }


def test_update_payload_preserves_existing_config_and_can_clear_folder() -> None:
    args = UpdateEntryInput(entry_id=4, port=2222, folder_id=None)
    existing = {
        "config": {
            "protocol": "ssh",
            "ip": "203.0.113.10",
            "port": 22,
            "keyboardLayout": "en-us",
        }
    }
    assert update_entry_payload(args, existing) == {
        "folderId": None,
        "config": {
            "protocol": "ssh",
            "ip": "203.0.113.10",
            "port": 2222,
            "keyboardLayout": "en-us",
        },
    }


def test_operation_paths_match_selected_nexterm_routes() -> None:
    assert OPERATION_BY_NAME["nexterm_list_tags"].path(OPERATION_BY_NAME["nexterm_list_tags"].model()) == "/api/tags/list"
    assert OPERATION_BY_NAME["nexterm_get_audit_logs"].method == "GET"
    assert OPERATION_BY_NAME["nexterm_create_source"].method == "POST"
    assert OPERATION_BY_NAME["nexterm_restore_backup"].destructive is True


def test_active_theme_requires_explicit_id_or_null() -> None:
    assert SetActiveThemeInput(theme_id=None).theme_id is None
    try:
        SetActiveThemeInput()
    except Exception:
        pass
    else:
        raise AssertionError("theme_id must be explicitly supplied, including null")
