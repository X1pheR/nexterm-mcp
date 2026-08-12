from __future__ import annotations

import asyncio
import json
from collections.abc import Sequence
from typing import Any, TypeVar

import mcp.types as types
from mcp.server import Server
from pydantic import BaseModel, ValidationError

from .client import NextermClient, NextermError
from .config import ConfigurationError, Settings
from .models import CreateEntryInput, EmptyInput, EntryIdInput, UpdateEntryInput

app = Server("nexterm")
_settings: Settings
ModelT = TypeVar("ModelT", bound=BaseModel)


def _annotations(*, read_only: bool, destructive: bool = False) -> types.ToolAnnotations:
    return types.ToolAnnotations(
        readOnlyHint=read_only,
        destructiveHint=destructive,
        idempotentHint=read_only,
        openWorldHint=True,
    )


def _tool(name: str, description: str, model: type[BaseModel], *, read_only: bool, destructive: bool = False) -> types.Tool:
    return types.Tool(
        name=name,
        description=description,
        inputSchema=model.model_json_schema(),
        annotations=_annotations(read_only=read_only, destructive=destructive),
    )


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        _tool("nexterm_status", "Verify authenticated Nexterm API access and report bounded adapter status without exposing credentials.", EmptyInput, read_only=True),
        _tool("nexterm_list_entries", "List Nexterm entries accessible to the configured account. Sensitive credential-shaped fields are removed defensively.", EmptyInput, read_only=True),
        _tool("nexterm_get_entry", "Get one Nexterm entry by numeric ID. Sensitive credential-shaped fields are removed defensively.", EntryIdInput, read_only=True),
        _tool("nexterm_list_identities", "List existing Nexterm identity metadata for selecting identity IDs. Credential material is never returned.", EmptyInput, read_only=True),
        _tool("nexterm_list_folders", "List existing Nexterm folders for selecting folder IDs.", EmptyInput, read_only=True),
        _tool("nexterm_create_entry", "Create a bounded Nexterm server entry. Mutations must be explicitly enabled in server configuration.", CreateEntryInput, read_only=False),
        _tool("nexterm_update_entry", "Update supported fields on one Nexterm server entry. Mutations must be explicitly enabled in server configuration.", UpdateEntryInput, read_only=False),
        _tool("nexterm_delete_entry", "Permanently delete one Nexterm entry by numeric ID. Mutations must be explicitly enabled in server configuration.", EntryIdInput, read_only=False, destructive=True),
    ]


def _validate(model: type[ModelT], arguments: Any) -> ModelT:
    return model.model_validate(arguments or {})


def _json_result(value: Any) -> Sequence[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))]


def _client() -> NextermClient:
    return NextermClient(_settings)


def _require_mutations() -> None:
    if not _settings.mutations_enabled:
        raise RuntimeError("Nexterm mutations are disabled; set NEXTERM_MUTATIONS_ENABLED=true in the MCP server environment")


def _create_payload(args: CreateEntryInput) -> dict[str, Any]:
    config: dict[str, Any] = {"protocol": args.protocol, "ip": args.ip}
    if args.port is not None:
        config["port"] = args.port
    if args.monitoring_enabled is not None:
        config["monitoringEnabled"] = args.monitoring_enabled
    payload: dict[str, Any] = {"name": args.name, "type": "server", "config": config}
    if args.identity_ids:
        payload["identities"] = args.identity_ids
    if args.folder_id is not None:
        payload["folderId"] = args.folder_id
    if args.organization_id is not None:
        payload["organizationId"] = args.organization_id
    if args.icon is not None:
        payload["icon"] = args.icon
    return payload


def _update_payload(args: UpdateEntryInput, existing_entry: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    config_changes: dict[str, Any] = {}
    if args.name is not None:
        payload["name"] = args.name
    if args.protocol is not None:
        config_changes["protocol"] = args.protocol
    if args.ip is not None:
        config_changes["ip"] = args.ip
    if args.port is not None:
        config_changes["port"] = args.port
    if args.monitoring_enabled is not None:
        config_changes["monitoringEnabled"] = args.monitoring_enabled
    if config_changes:
        existing_config = (existing_entry or {}).get("config", {})
        if not isinstance(existing_config, dict):
            raise ValueError("Existing Nexterm entry has no object config; refusing unsafe partial update")
        payload["config"] = {**existing_config, **config_changes}
    if args.identity_ids is not None:
        payload["identities"] = args.identity_ids
    if args.folder_id is not None:
        payload["folderId"] = args.folder_id
    if args.organization_id is not None:
        payload["organizationId"] = args.organization_id
    if args.icon is not None:
        payload["icon"] = args.icon
    if not payload:
        raise ValueError("At least one field must be supplied for an update")
    return payload


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        client = _client()
        if name == "nexterm_status":
            _validate(EmptyInput, arguments)
            entries = client.list_entries()
            count = len(entries) if isinstance(entries, list) else None
            result = {"ready": True, "baseUrl": _settings.base_url, "mutationsEnabled": _settings.mutations_enabled, "entryCount": count}
        elif name == "nexterm_list_entries":
            _validate(EmptyInput, arguments)
            result = client.list_entries()
        elif name == "nexterm_get_entry":
            args = _validate(EntryIdInput, arguments)
            result = client.get_entry(args.entry_id)
        elif name == "nexterm_list_identities":
            _validate(EmptyInput, arguments)
            result = client.list_identities()
        elif name == "nexterm_list_folders":
            _validate(EmptyInput, arguments)
            result = client.list_folders()
        elif name == "nexterm_create_entry":
            args = _validate(CreateEntryInput, arguments)
            _require_mutations()
            result = client.create_entry(_create_payload(args))
        elif name == "nexterm_update_entry":
            args = _validate(UpdateEntryInput, arguments)
            _require_mutations()
            existing = client.get_entry(args.entry_id)
            if not isinstance(existing, dict):
                raise RuntimeError("Nexterm returned an invalid entry object; refusing update")
            result = client.update_entry(args.entry_id, _update_payload(args, existing))
        elif name == "nexterm_delete_entry":
            args = _validate(EntryIdInput, arguments)
            _require_mutations()
            result = client.delete_entry(args.entry_id)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except ValidationError as error:
        raise ValueError(f"Invalid tool input: {error}") from None
    except (NextermError, ConfigurationError, ValueError, RuntimeError) as error:
        raise RuntimeError(str(error)) from None
    return _json_result(result)


async def run_stdio(settings: Settings) -> None:
    from mcp.server.stdio import stdio_server

    global _settings
    _settings = settings
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main() -> None:
    settings = Settings.from_env()
    asyncio.run(run_stdio(settings))
