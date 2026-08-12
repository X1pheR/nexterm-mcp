from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EmptyInput(StrictModel):
    pass


Protocol = Literal["ssh", "telnet", "rdp", "vnc", "sftp", "ftp", "ftps", "demo"]
RdpSecurity = Literal["any", "nla", "tls", "rdp", "vmconnect", ""]
EntryType = Literal["server", "pve-shell", "pve-lxc", "pve-qemu"]
MonitoringTimeRange = Literal["1h", "6h", "24h"]


class RecentEntriesInput(StrictModel):
    limit: int = Field(default=5, ge=1)


class EntryIdInput(StrictModel):
    entry_id: int = Field(ge=1)


class CreateEntryInput(StrictModel):
    name: str = Field(min_length=1)
    protocol: Protocol = "ssh"
    ip: str = Field(min_length=1)
    port: int | None = Field(default=None, ge=1, le=65535)
    keyboard_layout: str | None = None
    monitoring_enabled: bool | None = None
    node_name: str | None = None
    vmid: int | str | None = None
    rdp_security: RdpSecurity | None = None
    jump_host_ids: list[int] | None = None
    mac_address: str | None = Field(default=None, pattern=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^$")
    wake_on_lan_enabled: bool | None = None
    wol_broadcast_address: str | None = None
    identity_ids: list[int] = Field(default_factory=list)
    folder_id: int | None = Field(default=None, ge=1)
    organization_id: int | None = Field(default=None, ge=1)
    icon: str | None = None
    renderer: str | None = None


class UpdateEntryInput(StrictModel):
    entry_id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1)
    entry_type: EntryType | None = None
    protocol: Protocol | None = None
    ip: str | None = Field(default=None, min_length=1)
    port: int | None = Field(default=None, ge=1, le=65535)
    keyboard_layout: str | None = None
    monitoring_enabled: bool | None = None
    node_name: str | None = None
    vmid: int | str | None = None
    rdp_security: RdpSecurity | None = None
    jump_host_ids: list[int] | None = None
    mac_address: str | None = Field(default=None, pattern=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^$")
    wake_on_lan_enabled: bool | None = None
    wol_broadcast_address: str | None = None
    identity_ids: list[int] | None = None
    folder_id: int | None = Field(default=None, ge=1)
    organization_id: int | None = Field(default=None, ge=1)
    icon: str | None = None
    renderer: str | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateEntryInput":
        if self.model_fields_set <= {"entry_id"}:
            raise ValueError("At least one entry field must be supplied")
        return self


class RepositionEntryInput(StrictModel):
    entry_id: int = Field(ge=1)
    placement: Literal["before", "after"]
    target_id: int | None = Field(default=None, ge=1)
    folder_id: int | None = Field(default=None, ge=1)
    organization_id: int | None = Field(default=None, ge=1)


class SSHImportServerInput(StrictModel):
    name: str = Field(min_length=1)
    ip: str = Field(min_length=1)
    port: int = Field(default=22, ge=1, le=65535)
    identity_ids: list[int] = Field(default_factory=list)
    keyboard_layout: str | None = None
    jump_host_ids: list[int] | None = None


class ImportSSHConfigInput(StrictModel):
    servers: list[SSHImportServerInput] = Field(min_length=1)
    folder_id: int | None = Field(default=None, ge=1)


class FolderIdInput(StrictModel):
    folder_id: int = Field(ge=1)


class CreateFolderInput(StrictModel):
    name: str = Field(min_length=1, max_length=50)
    parent_id: int | None = Field(default=None, ge=1)
    organization_id: int | None = Field(default=None, ge=1)


class UpdateFolderInput(StrictModel):
    folder_id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=50)
    parent_id: int | None = Field(default=None, ge=1)
    organization_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def require_change(self) -> "UpdateFolderInput":
        if self.model_fields_set <= {"folder_id"}:
            raise ValueError("At least one folder field must be supplied")
        return self


class TagIdInput(StrictModel):
    tag_id: int = Field(ge=1)


class EntryTagInput(StrictModel):
    entry_id: int = Field(ge=1)
    tag_id: int = Field(ge=1)


class CreateTagInput(StrictModel):
    name: str = Field(min_length=1)
    color: str = Field(min_length=1)


class UpdateTagInput(StrictModel):
    tag_id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1)
    color: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_change(self) -> "UpdateTagInput":
        if self.model_fields_set <= {"tag_id"}:
            raise ValueError("At least one tag field must be supplied")
        return self


class OrganizationIdInput(StrictModel):
    organization_id: int = Field(ge=1)


class OrganizationMemberInput(StrictModel):
    organization_id: int = Field(ge=1)
    account_id: int = Field(ge=1)


class CreateOrganizationInput(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class UpdateOrganizationInput(StrictModel):
    organization_id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def require_change(self) -> "UpdateOrganizationInput":
        if self.model_fields_set <= {"organization_id"}:
            raise ValueError("At least one organization field must be supplied")
        return self


class UpdateOrganizationSessionSettingsInput(StrictModel):
    organization_id: int = Field(ge=1)
    enable_live_session_sharing: bool


class ScriptListInput(StrictModel):
    search: str | None = None
    organization_id: int | None = Field(default=None, ge=1)


class ScriptIdInput(StrictModel):
    script_id: int = Field(ge=1)
    organization_id: int | None = Field(default=None, ge=1)


class CreateScriptInput(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    description: str | None = None
    organization_id: int | None = Field(default=None, ge=1)
    os_filter: list[str] | None = None


class UpdateScriptInput(StrictModel):
    script_id: int = Field(ge=1)
    organization_id: int | None = Field(default=None, ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)
    description: str | None = None
    os_filter: list[str] | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateScriptInput":
        if self.model_fields_set <= {"script_id", "organization_id"}:
            raise ValueError("At least one script field must be supplied")
        return self


class RepositionScriptInput(StrictModel):
    script_id: int = Field(ge=1)
    target_id: int = Field(ge=1)
    organization_id: int | None = Field(default=None, ge=1)


class SnippetIdInput(StrictModel):
    snippet_id: int = Field(ge=1)
    organization_id: int | None = Field(default=None, ge=1)


class CreateSnippetInput(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    command: str = Field(min_length=1)
    description: str | None = None
    organization_id: int | None = Field(default=None, ge=1)
    os_filter: list[str] | None = None


class UpdateSnippetInput(StrictModel):
    snippet_id: int = Field(ge=1)
    organization_id: int | None = Field(default=None, ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    command: str | None = Field(default=None, min_length=1)
    description: str | None = None
    os_filter: list[str] | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateSnippetInput":
        if self.model_fields_set <= {"snippet_id", "organization_id"}:
            raise ValueError("At least one snippet field must be supplied")
        return self


class RepositionSnippetInput(StrictModel):
    snippet_id: int = Field(ge=1)
    target_id: int = Field(ge=1)
    organization_id: int | None = Field(default=None, ge=1)


class ThemeIdInput(StrictModel):
    theme_id: int = Field(ge=1)


class CreateThemeInput(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    css: str = Field(min_length=1, max_length=100000)
    description: str | None = Field(default=None, max_length=1000)


class UpdateThemeInput(StrictModel):
    theme_id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    css: str | None = Field(default=None, min_length=1, max_length=100000)
    description: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def require_change(self) -> "UpdateThemeInput":
        if self.model_fields_set <= {"theme_id"}:
            raise ValueError("At least one theme field must be supplied")
        return self


class SetActiveThemeInput(StrictModel):
    theme_id: int | None = Field(ge=1)


class SourceIdInput(StrictModel):
    source_id: int = Field(ge=1)


class ValidateSourceInput(StrictModel):
    url: str = Field(min_length=1)


class CreateSourceInput(StrictModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1)


class UpdateSourceInput(StrictModel):
    source_id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: str | None = Field(default=None, min_length=1)
    enabled: bool | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateSourceInput":
        if self.model_fields_set <= {"source_id"}:
            raise ValueError("At least one source field must be supplied")
        return self


class MonitoringTargetInput(StrictModel):
    target_id: int = Field(ge=1)
    time_range: MonitoringTimeRange = "1h"


class UpdateMonitoringSettingsInput(StrictModel):
    status_checker_enabled: bool | None = None
    status_interval: int | None = Field(default=None, ge=10, le=300)
    monitoring_enabled: bool | None = None
    monitoring_interval: int | None = Field(default=None, ge=30, le=600)
    data_retention_hours: int | None = Field(default=None, ge=1, le=24)
    connection_timeout: int | None = Field(default=None, ge=5, le=120)
    batch_size: int | None = Field(default=None, ge=1, le=50)

    @model_validator(mode="after")
    def require_change(self) -> "UpdateMonitoringSettingsInput":
        if not self.model_fields_set:
            raise ValueError("At least one monitoring setting must be supplied")
        return self


class AuditLogsInput(StrictModel):
    organization_id: int | Literal["personal"] | None = None
    action: str | None = Field(default=None, max_length=100)
    resource: str | None = Field(default=None, max_length=50)
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class UpdateOrganizationAuditSettingsInput(StrictModel):
    organization_id: int = Field(ge=1)
    require_connection_reason: bool | None = None
    enable_file_operation_audit: bool | None = None
    enable_server_connection_audit: bool | None = None
    enable_identity_management_audit: bool | None = None
    enable_identity_credentials_access_audit: bool | None = None
    enable_server_management_audit: bool | None = None
    enable_folder_management_audit: bool | None = None
    enable_script_execution_audit: bool | None = None
    enable_ai_operation_audit: bool | None = None
    enable_session_recording: bool | None = None
    recording_retention_days: int | None = Field(default=None, ge=1, le=3650)

    @model_validator(mode="after")
    def require_change(self) -> "UpdateOrganizationAuditSettingsInput":
        if self.model_fields_set <= {"organization_id"}:
            raise ValueError("At least one audit setting must be supplied")
        return self


class BackupFileTypeInput(StrictModel):
    file_type: Literal["recordings", "logs"]


class DeleteBackupFileInput(BackupFileTypeInput):
    filename: str = Field(min_length=1)


class UpdateBackupSettingsInput(StrictModel):
    schedule_interval: int | None = None
    retention: int | None = None
    include_database: bool | None = None
    include_recordings: bool | None = None
    include_logs: bool | None = None

    @model_validator(mode="after")
    def require_change(self) -> "UpdateBackupSettingsInput":
        if not self.model_fields_set:
            raise ValueError("At least one backup setting must be supplied")
        return self


class BackupProviderInput(StrictModel):
    provider_id: str = Field(min_length=1)


class RestoreBackupInput(BackupProviderInput):
    backup_name: str = Field(min_length=1)


class IntegrationIdInput(StrictModel):
    integration_id: int = Field(ge=1)


class IntegrationEntryInput(StrictModel):
    entry_id: int = Field(ge=1)
