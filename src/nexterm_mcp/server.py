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
from .models import EmptyInput, UpdateEntryInput
from .operations import OPERATION_BY_NAME, OPERATIONS, Operation, update_entry_payload

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


def _tool(operation: Operation) -> types.Tool:
    return types.Tool(
        name=operation.name,
        description=operation.description,
        inputSchema=operation.model.model_json_schema(),
        annotations=_annotations(read_only=operation.read_only, destructive=operation.destructive),
    )


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    status = types.Tool(
        name="nexterm_status",
        description="Verify authenticated Nexterm API access and report adapter status without exposing credentials.",
        inputSchema=EmptyInput.model_json_schema(),
        annotations=_annotations(read_only=True),
    )
    return [status, *(_tool(operation) for operation in OPERATIONS)]


def _validate(model: type[ModelT], arguments: Any) -> ModelT:
    return model.model_validate(arguments or {})


def _json_result(value: Any) -> Sequence[types.TextContent]:
    return [types.TextContent(type="text", text=json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))]


def _client() -> NextermClient:
    return NextermClient(_settings)


def _require_mutations() -> None:
    if not _settings.mutations_enabled:
        raise RuntimeError("Nexterm mutations are disabled; set NEXTERM_MUTATIONS_ENABLED=true in the MCP server environment")


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    try:
        client = _client()
        if name == "nexterm_status":
            _validate(EmptyInput, arguments)
            client.request("GET", "/api/accounts/me")
            service = client.request("GET", "/api/service/version")
            service_version = service.get("version") if isinstance(service, dict) else None
            result = {
                "ready": True,
                "baseUrl": _settings.base_url,
                "mutationsEnabled": _settings.mutations_enabled,
                "toolCount": 1 + len(OPERATIONS),
                "compatibilityBaseline": "Nexterm v1.2.2-BETA",
                "serviceVersion": service_version,
            }
        else:
            operation = OPERATION_BY_NAME.get(name)
            if operation is None:
                raise ValueError(f"Unknown tool: {name}")
            args = _validate(operation.model, arguments)
            if not operation.read_only:
                _require_mutations()

            if name == "nexterm_update_entry":
                typed_args = UpdateEntryInput.model_validate(args)
                existing = client.get_entry(typed_args.entry_id)
                if not isinstance(existing, dict):
                    raise RuntimeError("Nexterm returned an invalid entry object; refusing update")
                payload = update_entry_payload(typed_args, existing)
            else:
                payload = operation.payload(args) if operation.payload else None

            query = operation.query(args) if operation.query else None
            result = client.request(operation.method, operation.path(args), payload=payload, query=query)
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
