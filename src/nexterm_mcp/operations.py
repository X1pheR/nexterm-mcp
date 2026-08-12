from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable
from urllib.parse import quote

from pydantic import BaseModel

from .models import (
    AuditLogsInput,
    BackupFileTypeInput,
    BackupProviderInput,
    CreateEntryInput,
    CreateFolderInput,
    CreateOrganizationInput,
    CreateScriptInput,
    CreateSnippetInput,
    CreateSourceInput,
    CreateTagInput,
    CreateThemeInput,
    DeleteBackupFileInput,
    EmptyInput,
    EntryIdInput,
    EntryTagInput,
    FolderIdInput,
    ImportSSHConfigInput,
    IntegrationEntryInput,
    IntegrationIdInput,
    MonitoringTargetInput,
    OrganizationIdInput,
    OrganizationMemberInput,
    RecentEntriesInput,
    RepositionEntryInput,
    RepositionScriptInput,
    RepositionSnippetInput,
    RestoreBackupInput,
    ScriptIdInput,
    ScriptListInput,
    SetActiveThemeInput,
    SnippetIdInput,
    SourceIdInput,
    TagIdInput,
    ThemeIdInput,
    UpdateBackupSettingsInput,
    UpdateEntryInput,
    UpdateFolderInput,
    UpdateMonitoringSettingsInput,
    UpdateOrganizationAuditSettingsInput,
    UpdateOrganizationInput,
    UpdateOrganizationSessionSettingsInput,
    UpdateScriptInput,
    UpdateSnippetInput,
    UpdateSourceInput,
    UpdateTagInput,
    UpdateThemeInput,
    ValidateSourceInput,
)

PathBuilder = Callable[[BaseModel], str]
DataBuilder = Callable[[BaseModel], dict[str, Any] | None]


@dataclass(frozen=True)
class Operation:
    name: str
    description: str
    model: type[BaseModel]
    method: str
    path: PathBuilder
    read_only: bool
    destructive: bool = False
    payload: DataBuilder | None = None
    query: DataBuilder | None = None


def fixed(path: str) -> PathBuilder:
    return lambda _args: path


def _mapped(
    model: BaseModel,
    mapping: dict[str, str],
    *,
    always: set[str] | None = None,
    include_none: set[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    always = always or set()
    include_none = include_none or set()
    for source, target in mapping.items():
        if source not in always and source not in model.model_fields_set:
            continue
        value = getattr(model, source)
        if value is None and source not in include_none:
            continue
        if isinstance(value, datetime):
            value = value.isoformat()
        result[target] = value
    return result


ENTRY_CONFIG_FIELDS = {
    "protocol": "protocol",
    "ip": "ip",
    "port": "port",
    "keyboard_layout": "keyboardLayout",
    "monitoring_enabled": "monitoringEnabled",
    "node_name": "nodeName",
    "vmid": "vmid",
    "rdp_security": "rdpSecurity",
    "jump_host_ids": "jumpHosts",
    "mac_address": "macAddress",
    "wake_on_lan_enabled": "wakeOnLanEnabled",
    "wol_broadcast_address": "wolBroadcastAddress",
}


def create_entry_payload(model: BaseModel) -> dict[str, Any]:
    args = CreateEntryInput.model_validate(model)
    config: dict[str, Any] = {"protocol": args.protocol, "ip": args.ip}
    for source, target in ENTRY_CONFIG_FIELDS.items():
        if source in {"protocol", "ip"}:
            continue
        value = getattr(args, source)
        if value is not None:
            config[target] = value
    payload: dict[str, Any] = {"name": args.name, "type": "server", "config": config}
    if args.identity_ids:
        payload["identities"] = args.identity_ids
    payload.update(
        _mapped(
            args,
            {
                "folder_id": "folderId",
                "organization_id": "organizationId",
                "icon": "icon",
                "renderer": "renderer",
            },
        )
    )
    return payload


def update_entry_payload(args: UpdateEntryInput, existing_entry: dict[str, Any]) -> dict[str, Any]:
    payload = _mapped(
        args,
        {
            "name": "name",
            "entry_type": "type",
            "identity_ids": "identities",
            "folder_id": "folderId",
            "organization_id": "organizationId",
            "icon": "icon",
            "renderer": "renderer",
        },
        include_none={"folder_id", "organization_id"},
    )
    config_changes = _mapped(args, ENTRY_CONFIG_FIELDS)
    if config_changes:
        existing_config = existing_entry.get("config", {})
        if not isinstance(existing_config, dict):
            raise ValueError("Existing Nexterm entry has no object config; refusing unsafe partial update")
        payload["config"] = {**existing_config, **config_changes}
    if not payload:
        raise ValueError("At least one entry field must be supplied")
    return payload


def import_ssh_payload(model: BaseModel) -> dict[str, Any]:
    args = ImportSSHConfigInput.model_validate(model)
    servers: list[dict[str, Any]] = []
    for server in args.servers:
        config: dict[str, Any] = {}
        if server.keyboard_layout is not None:
            config["keyboardLayout"] = server.keyboard_layout
        if server.jump_host_ids is not None:
            config["jumpHosts"] = server.jump_host_ids
        item: dict[str, Any] = {"name": server.name, "ip": server.ip, "port": server.port}
        if server.identity_ids:
            item["identities"] = server.identity_ids
        if config:
            item["config"] = config
        servers.append(item)
    return {"servers": servers, "folderId": args.folder_id}


def reposition_entry_payload(model: BaseModel) -> dict[str, Any]:
    args = RepositionEntryInput.model_validate(model)
    return _mapped(
        args,
        {
            "placement": "placement",
            "target_id": "targetId",
            "folder_id": "folderId",
            "organization_id": "organizationId",
        },
        always={"placement"},
    )


def folder_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {"name": "name", "parent_id": "parentId", "organization_id": "organizationId"},
        include_none={"parent_id", "organization_id"},
    )


def tag_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(model, {"name": "name", "color": "color"})


def organization_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {"name": "name", "description": "description"},
        include_none={"description"},
    )


def organization_session_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(model, {"enable_live_session_sharing": "enableLiveSessionSharing"}, always={"enable_live_session_sharing"})


def script_query(model: BaseModel) -> dict[str, Any]:
    return _mapped(model, {"search": "search", "organization_id": "organizationId"})


def organization_query(model: BaseModel) -> dict[str, Any]:
    return _mapped(model, {"organization_id": "organizationId"})


def script_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {
            "name": "name",
            "content": "content",
            "description": "description",
            "organization_id": "organizationId",
            "os_filter": "osFilter",
        },
        include_none={"description", "organization_id", "os_filter"},
    )


def script_update_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {"name": "name", "content": "content", "description": "description", "os_filter": "osFilter"},
        include_none={"description", "os_filter"},
    )


def snippet_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {
            "name": "name",
            "command": "command",
            "description": "description",
            "organization_id": "organizationId",
            "os_filter": "osFilter",
        },
        include_none={"description", "organization_id", "os_filter"},
    )


def snippet_update_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {"name": "name", "command": "command", "description": "description", "os_filter": "osFilter"},
        include_none={"description", "os_filter"},
    )


def theme_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {"name": "name", "css": "css", "description": "description"},
        include_none={"description"},
    )


def source_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(model, {"name": "name", "url": "url", "enabled": "enabled"})


def monitoring_query(model: BaseModel) -> dict[str, Any]:
    args = MonitoringTargetInput.model_validate(model)
    return {"timeRange": args.time_range}


def monitoring_settings_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {
            "status_checker_enabled": "statusCheckerEnabled",
            "status_interval": "statusInterval",
            "monitoring_enabled": "monitoringEnabled",
            "monitoring_interval": "monitoringInterval",
            "data_retention_hours": "dataRetentionHours",
            "connection_timeout": "connectionTimeout",
            "batch_size": "batchSize",
        },
    )


def audit_query(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {
            "organization_id": "organizationId",
            "action": "action",
            "resource": "resource",
            "start_date": "startDate",
            "end_date": "endDate",
            "limit": "limit",
            "offset": "offset",
        },
        always={"limit", "offset"},
    )


def audit_settings_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {
            "require_connection_reason": "requireConnectionReason",
            "enable_file_operation_audit": "enableFileOperationAudit",
            "enable_server_connection_audit": "enableServerConnectionAudit",
            "enable_identity_management_audit": "enableIdentityManagementAudit",
            "enable_identity_credentials_access_audit": "enableIdentityCredentialsAccessAudit",
            "enable_server_management_audit": "enableServerManagementAudit",
            "enable_folder_management_audit": "enableFolderManagementAudit",
            "enable_script_execution_audit": "enableScriptExecutionAudit",
            "enable_ai_operation_audit": "enableAIOperationAudit",
            "enable_session_recording": "enableSessionRecording",
            "recording_retention_days": "recordingRetentionDays",
        },
    )


def backup_settings_payload(model: BaseModel) -> dict[str, Any]:
    return _mapped(
        model,
        {
            "schedule_interval": "scheduleInterval",
            "retention": "retention",
            "include_database": "includeDatabase",
            "include_recordings": "includeRecordings",
            "include_logs": "includeLogs",
        },
    )


def validate_source_payload(model: BaseModel) -> dict[str, Any]:
    args = ValidateSourceInput.model_validate(model)
    return {"url": args.url}


def set_active_theme_payload(model: BaseModel) -> dict[str, Any]:
    args = SetActiveThemeInput.model_validate(model)
    return {"themeId": args.theme_id}


def _id_path(prefix: str, attr: str, suffix: str = "") -> PathBuilder:
    return lambda args: f"{prefix}/{quote(str(getattr(args, attr)), safe='')}{suffix}"


def _tool(
    name: str,
    description: str,
    model: type[BaseModel],
    method: str,
    path: PathBuilder,
    *,
    read_only: bool,
    destructive: bool = False,
    payload: DataBuilder | None = None,
    query: DataBuilder | None = None,
) -> Operation:
    return Operation(name, description, model, method, path, read_only, destructive, payload, query)


OPERATIONS: tuple[Operation, ...] = (
    # Entries
    _tool("nexterm_list_entries", "List accessible Nexterm entries.", EmptyInput, "GET", fixed("/api/entries/list"), read_only=True),
    _tool("nexterm_recent_entries", "List recently connected Nexterm entries.", RecentEntriesInput, "GET", fixed("/api/entries/recent"), read_only=True, query=lambda a: {"limit": a.limit}),
    _tool("nexterm_get_entry", "Get one Nexterm entry by ID.", EntryIdInput, "GET", _id_path("/api/entries", "entry_id"), read_only=True),
    _tool("nexterm_create_entry", "Create a Nexterm server entry using typed connection fields.", CreateEntryInput, "PUT", fixed("/api/entries"), read_only=False, payload=create_entry_payload),
    _tool("nexterm_update_entry", "Update typed fields on an entry while preserving unmodified Nexterm config fields.", UpdateEntryInput, "PATCH", _id_path("/api/entries", "entry_id"), read_only=False),
    _tool("nexterm_delete_entry", "Permanently delete a Nexterm entry.", EntryIdInput, "DELETE", _id_path("/api/entries", "entry_id"), read_only=False, destructive=True),
    _tool("nexterm_duplicate_entry", "Duplicate an existing Nexterm entry.", EntryIdInput, "POST", _id_path("/api/entries", "entry_id", "/duplicate"), read_only=False),
    _tool("nexterm_import_ssh_config", "Import a typed batch of SSH server definitions into a Nexterm folder.", ImportSSHConfigInput, "POST", fixed("/api/entries/import/ssh-config"), read_only=False, payload=import_ssh_payload),
    _tool("nexterm_reposition_entry", "Reposition or move a Nexterm entry.", RepositionEntryInput, "PATCH", _id_path("/api/entries", "entry_id", "/reposition"), read_only=False, payload=reposition_entry_payload),
    _tool("nexterm_wake_entry", "Send Wake-on-LAN for an entry using its configured WOL settings.", EntryIdInput, "POST", _id_path("/api/entries", "entry_id", "/wake"), read_only=False),
    # Identities (metadata only; credential-bearing mutations are intentionally excluded)
    _tool("nexterm_list_identities", "List accessible Nexterm identity metadata. Credential material is never returned.", EmptyInput, "GET", fixed("/api/identities/list"), read_only=True),
    # Folders
    _tool("nexterm_list_folders", "List accessible Nexterm folders.", EmptyInput, "GET", fixed("/api/folders/list"), read_only=True),
    _tool("nexterm_create_folder", "Create a Nexterm folder.", CreateFolderInput, "PUT", fixed("/api/folders"), read_only=False, payload=folder_payload),
    _tool("nexterm_update_folder", "Update or move a Nexterm folder.", UpdateFolderInput, "PATCH", _id_path("/api/folders", "folder_id"), read_only=False, payload=folder_payload),
    _tool("nexterm_delete_folder", "Permanently delete a Nexterm folder according to Nexterm's folder deletion semantics.", FolderIdInput, "DELETE", _id_path("/api/folders", "folder_id"), read_only=False, destructive=True),
    # Tags
    _tool("nexterm_list_tags", "List personal Nexterm tags.", EmptyInput, "GET", fixed("/api/tags/list"), read_only=True),
    _tool("nexterm_create_tag", "Create a Nexterm tag.", CreateTagInput, "PUT", fixed("/api/tags"), read_only=False, payload=tag_payload),
    _tool("nexterm_update_tag", "Update a Nexterm tag.", UpdateTagInput, "PATCH", _id_path("/api/tags", "tag_id"), read_only=False, payload=tag_payload),
    _tool("nexterm_delete_tag", "Permanently delete a Nexterm tag.", TagIdInput, "DELETE", _id_path("/api/tags", "tag_id"), read_only=False, destructive=True),
    _tool("nexterm_assign_tag", "Assign a tag to an entry.", EntryTagInput, "POST", lambda a: f"/api/tags/{a.tag_id}/assign/{a.entry_id}", read_only=False),
    _tool("nexterm_unassign_tag", "Remove a tag assignment from an entry.", EntryTagInput, "DELETE", lambda a: f"/api/tags/{a.tag_id}/assign/{a.entry_id}", read_only=False),
    _tool("nexterm_list_entry_tags", "List tags assigned to an entry.", EntryIdInput, "GET", _id_path("/api/tags/entry", "entry_id"), read_only=True),
    # Organizations: resource/settings management only; membership/authz mutations are intentionally excluded.
    _tool("nexterm_list_organizations", "List organizations accessible to the configured Nexterm account.", EmptyInput, "GET", fixed("/api/organizations"), read_only=True),
    _tool("nexterm_get_organization", "Get organization details.", OrganizationIdInput, "GET", _id_path("/api/organizations", "organization_id"), read_only=True),
    _tool("nexterm_create_organization", "Create a Nexterm organization.", CreateOrganizationInput, "PUT", fixed("/api/organizations"), read_only=False, payload=organization_payload),
    _tool("nexterm_update_organization", "Update organization name or description.", UpdateOrganizationInput, "PATCH", _id_path("/api/organizations", "organization_id"), read_only=False, payload=organization_payload),
    _tool("nexterm_delete_organization", "Permanently delete a Nexterm organization.", OrganizationIdInput, "DELETE", _id_path("/api/organizations", "organization_id"), read_only=False, destructive=True),
    _tool("nexterm_list_organization_members", "List members of an organization.", OrganizationIdInput, "GET", _id_path("/api/organizations", "organization_id", "/members"), read_only=True),
    _tool("nexterm_get_organization_member_permissions", "Read one organization's effective member permissions.", OrganizationMemberInput, "GET", lambda a: f"/api/organizations/{a.organization_id}/members/{a.account_id}/permissions", read_only=True),
    _tool("nexterm_get_organization_session_settings", "Read organization live-session settings.", OrganizationIdInput, "GET", _id_path("/api/organizations", "organization_id", "/session-settings"), read_only=True),
    _tool("nexterm_update_organization_session_settings", "Update organization live-session settings.", UpdateOrganizationSessionSettingsInput, "PATCH", _id_path("/api/organizations", "organization_id", "/session-settings"), read_only=False, payload=organization_session_payload),
    _tool("nexterm_list_pending_invitations", "List pending organization invitations for the configured account.", EmptyInput, "GET", fixed("/api/organizations/invitations/pending"), read_only=True),
    # Scripts
    _tool("nexterm_list_scripts", "List or search accessible scripts, optionally scoped to an organization.", ScriptListInput, "GET", fixed("/api/scripts"), read_only=True, query=script_query),
    _tool("nexterm_list_all_scripts", "List all accessible scripts across personal, organization and source scopes.", EmptyInput, "GET", fixed("/api/scripts/all"), read_only=True),
    _tool("nexterm_list_script_sources", "List source-backed scripts.", EmptyInput, "GET", fixed("/api/scripts/sources"), read_only=True),
    _tool("nexterm_get_script", "Get one script, optionally in an organization scope.", ScriptIdInput, "GET", _id_path("/api/scripts", "script_id"), read_only=True, query=organization_query),
    _tool("nexterm_create_script", "Create a Nexterm script. Script content is model-visible by design.", CreateScriptInput, "POST", fixed("/api/scripts"), read_only=False, payload=script_payload),
    _tool("nexterm_update_script", "Update a Nexterm script. Script content is model-visible by design.", UpdateScriptInput, "PUT", _id_path("/api/scripts", "script_id"), read_only=False, payload=script_update_payload, query=organization_query),
    _tool("nexterm_delete_script", "Permanently delete a Nexterm script.", ScriptIdInput, "DELETE", _id_path("/api/scripts", "script_id"), read_only=False, destructive=True, query=organization_query),
    _tool("nexterm_reposition_script", "Reorder a Nexterm script relative to another script.", RepositionScriptInput, "PATCH", _id_path("/api/scripts", "script_id", "/reposition"), read_only=False, payload=lambda a: {"targetId": a.target_id}, query=organization_query),
    # Snippets
    _tool("nexterm_list_snippets", "List all accessible Nexterm snippets.", EmptyInput, "GET", fixed("/api/snippets/all"), read_only=True),
    _tool("nexterm_list_snippet_sources", "List source-backed snippets.", EmptyInput, "GET", fixed("/api/snippets/sources"), read_only=True),
    _tool("nexterm_get_snippet", "Get one snippet, optionally in an organization scope.", SnippetIdInput, "GET", _id_path("/api/snippets", "snippet_id"), read_only=True, query=organization_query),
    _tool("nexterm_create_snippet", "Create a Nexterm command snippet. Command content is model-visible by design.", CreateSnippetInput, "PUT", fixed("/api/snippets"), read_only=False, payload=snippet_payload),
    _tool("nexterm_update_snippet", "Update a Nexterm command snippet.", UpdateSnippetInput, "PATCH", _id_path("/api/snippets", "snippet_id"), read_only=False, payload=snippet_update_payload, query=organization_query),
    _tool("nexterm_delete_snippet", "Permanently delete a Nexterm snippet.", SnippetIdInput, "DELETE", _id_path("/api/snippets", "snippet_id"), read_only=False, destructive=True, query=organization_query),
    _tool("nexterm_reposition_snippet", "Reorder a Nexterm snippet relative to another snippet.", RepositionSnippetInput, "PATCH", _id_path("/api/snippets", "snippet_id", "/reposition"), read_only=False, payload=lambda a: {"targetId": a.target_id}, query=organization_query),
    # Themes
    _tool("nexterm_list_themes", "List available Nexterm themes.", EmptyInput, "GET", fixed("/api/themes"), read_only=True),
    _tool("nexterm_get_active_theme_css", "Get CSS for the configured account's active theme.", EmptyInput, "GET", fixed("/api/themes/active/css"), read_only=True),
    _tool("nexterm_get_theme", "Get theme metadata and content.", ThemeIdInput, "GET", _id_path("/api/themes", "theme_id"), read_only=True),
    _tool("nexterm_get_theme_css", "Get CSS for one theme.", ThemeIdInput, "GET", _id_path("/api/themes", "theme_id", "/css"), read_only=True),
    _tool("nexterm_create_theme", "Create a custom Nexterm CSS theme.", CreateThemeInput, "PUT", fixed("/api/themes"), read_only=False, payload=theme_payload),
    _tool("nexterm_update_theme", "Update a custom Nexterm CSS theme.", UpdateThemeInput, "PATCH", _id_path("/api/themes", "theme_id"), read_only=False, payload=theme_payload),
    _tool("nexterm_delete_theme", "Permanently delete a custom Nexterm theme.", ThemeIdInput, "DELETE", _id_path("/api/themes", "theme_id"), read_only=False, destructive=True),
    _tool("nexterm_set_active_theme", "Set an active theme, or pass null to clear the active theme.", SetActiveThemeInput, "PUT", fixed("/api/themes/active"), read_only=False, payload=set_active_theme_payload),
    # Sources
    _tool("nexterm_list_sources", "List configured Nexterm content sources.", EmptyInput, "GET", fixed("/api/sources"), read_only=True),
    _tool("nexterm_get_source", "Get one Nexterm content source.", SourceIdInput, "GET", _id_path("/api/sources", "source_id"), read_only=True),
    _tool("nexterm_validate_source", "Validate a source URL and report discovered content counts.", ValidateSourceInput, "POST", fixed("/api/sources/validate"), read_only=True, payload=validate_source_payload),
    _tool("nexterm_create_source", "Create and initially sync a Nexterm content source.", CreateSourceInput, "POST", fixed("/api/sources"), read_only=False, payload=source_payload),
    _tool("nexterm_update_source", "Update a Nexterm content source.", UpdateSourceInput, "PATCH", _id_path("/api/sources", "source_id"), read_only=False, payload=source_payload),
    _tool("nexterm_delete_source", "Permanently delete a source and its synchronized content.", SourceIdInput, "DELETE", _id_path("/api/sources", "source_id"), read_only=False, destructive=True),
    _tool("nexterm_sync_source", "Synchronize one Nexterm content source.", SourceIdInput, "POST", _id_path("/api/sources", "source_id", "/sync"), read_only=False),
    _tool("nexterm_sync_all_sources", "Trigger synchronization for all enabled content sources.", EmptyInput, "POST", fixed("/api/sources/sync-all"), read_only=False),
    # Monitoring
    _tool("nexterm_get_monitoring", "Get current monitoring overview for accessible servers.", EmptyInput, "GET", fixed("/api/monitoring"), read_only=True),
    _tool("nexterm_get_monitoring_settings", "Get global Nexterm monitoring settings.", EmptyInput, "GET", fixed("/api/monitoring/settings/global"), read_only=True),
    _tool("nexterm_update_monitoring_settings", "Update global Nexterm monitoring settings.", UpdateMonitoringSettingsInput, "PATCH", fixed("/api/monitoring/settings/global"), read_only=False, payload=monitoring_settings_payload),
    _tool("nexterm_get_integration_monitoring", "Get monitoring history for an integration.", MonitoringTargetInput, "GET", lambda a: f"/api/monitoring/integration/{a.target_id}", read_only=True, query=monitoring_query),
    _tool("nexterm_get_server_monitoring", "Get monitoring history for a server entry.", MonitoringTargetInput, "GET", lambda a: f"/api/monitoring/{a.target_id}", read_only=True, query=monitoring_query),
    # Audit (binary recording download is intentionally excluded)
    _tool("nexterm_get_audit_logs", "Query Nexterm audit logs with bounded pagination and filters.", AuditLogsInput, "GET", fixed("/api/audit/logs"), read_only=True, query=audit_query),
    _tool("nexterm_get_audit_metadata", "Get available audit actions and resource metadata.", EmptyInput, "GET", fixed("/api/audit/metadata"), read_only=True),
    _tool("nexterm_get_organization_audit_settings", "Get audit settings for an organization.", OrganizationIdInput, "GET", lambda a: f"/api/audit/organizations/{a.organization_id}/settings", read_only=True),
    _tool("nexterm_update_organization_audit_settings", "Update audit settings for an organization.", UpdateOrganizationAuditSettingsInput, "PATCH", lambda a: f"/api/audit/organizations/{a.organization_id}/settings", read_only=False, payload=audit_settings_payload),
    # Backup. Provider create/update are excluded because their API accepts plaintext passwords.
    _tool("nexterm_list_backup_files", "List Nexterm recording or log files available to the backup subsystem.", BackupFileTypeInput, "GET", lambda a: f"/api/backup/files/{a.file_type}", read_only=True),
    _tool("nexterm_delete_backup_file", "Permanently delete a Nexterm recording or log file.", DeleteBackupFileInput, "DELETE", lambda a: f"/api/backup/files/{a.file_type}/{quote(a.filename, safe='')}", read_only=False, destructive=True),
    _tool("nexterm_get_backup_settings", "Get backup settings and sanitized provider metadata.", EmptyInput, "GET", fixed("/api/backup/settings"), read_only=True),
    _tool("nexterm_update_backup_settings", "Update Nexterm backup schedule and inclusion settings.", UpdateBackupSettingsInput, "PATCH", fixed("/api/backup/settings"), read_only=False, payload=backup_settings_payload),
    _tool("nexterm_get_backup_storage", "Get Nexterm backup storage statistics.", EmptyInput, "GET", fixed("/api/backup/storage"), read_only=True),
    _tool("nexterm_delete_backup_provider", "Permanently delete a configured backup provider. Provider credential creation/update is intentionally not exposed.", BackupProviderInput, "DELETE", _id_path("/api/backup/providers", "provider_id"), read_only=False, destructive=True),
    _tool("nexterm_list_provider_backups", "List backups stored by one configured provider.", BackupProviderInput, "GET", _id_path("/api/backup/providers", "provider_id", "/backups"), read_only=True),
    _tool("nexterm_create_backup", "Create a backup using an existing configured provider.", BackupProviderInput, "POST", _id_path("/api/backup/providers", "provider_id", "/backups"), read_only=False),
    _tool("nexterm_restore_backup", "Restore a backup. Nexterm documents that this initiates a server restart.", RestoreBackupInput, "POST", lambda a: f"/api/backup/providers/{quote(a.provider_id, safe='')}/backups/{quote(a.backup_name, safe='')}/restore", read_only=False, destructive=True),
    # Proxmox integrations. Create/update are excluded because Nexterm requires a plaintext password.
    _tool("nexterm_get_integration", "Get sanitized metadata for one Nexterm integration.", IntegrationIdInput, "GET", _id_path("/api/integrations", "integration_id"), read_only=True),
    _tool("nexterm_delete_integration", "Permanently delete a Nexterm integration.", IntegrationIdInput, "DELETE", _id_path("/api/integrations", "integration_id"), read_only=False, destructive=True),
    _tool("nexterm_sync_integration", "Synchronize an existing Nexterm integration.", IntegrationIdInput, "POST", _id_path("/api/integrations", "integration_id", "/sync"), read_only=False),
    _tool("nexterm_start_integration_entry", "Start the external resource represented by an integration entry.", IntegrationEntryInput, "POST", _id_path("/api/integrations/entry", "entry_id", "/start"), read_only=False),
    _tool("nexterm_stop_integration_entry", "Stop the external resource represented by an integration entry.", IntegrationEntryInput, "POST", _id_path("/api/integrations/entry", "entry_id", "/stop"), read_only=False, destructive=True),
    _tool("nexterm_shutdown_integration_entry", "Request guest shutdown for the external resource represented by an integration entry.", IntegrationEntryInput, "POST", _id_path("/api/integrations/entry", "entry_id", "/shutdown"), read_only=False, destructive=True),
    # Engines: token-bearing create/regenerate endpoints are intentionally excluded.
    _tool("nexterm_list_engines", "List Nexterm engine metadata. Token-bearing engine mutations are intentionally excluded.", EmptyInput, "GET", fixed("/api/engines"), read_only=True),
)

OPERATION_BY_NAME = {operation.name: operation for operation in OPERATIONS}
