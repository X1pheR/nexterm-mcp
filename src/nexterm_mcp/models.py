from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EmptyInput(StrictModel):
    pass


class EntryIdInput(StrictModel):
    entry_id: int = Field(ge=1)


class CreateEntryInput(StrictModel):
    name: str = Field(min_length=1, max_length=256)
    protocol: Literal["ssh", "telnet", "rdp", "vnc", "sftp", "ftp", "ftps"] = "ssh"
    ip: str = Field(min_length=1, max_length=512)
    port: int | None = Field(default=None, ge=1, le=65535)
    identity_ids: list[int] = Field(default_factory=list)
    folder_id: int | None = Field(default=None, ge=1)
    organization_id: int | None = Field(default=None, ge=1)
    monitoring_enabled: bool | None = None
    icon: str | None = Field(default=None, max_length=256)


class UpdateEntryInput(StrictModel):
    entry_id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=256)
    protocol: Literal["ssh", "telnet", "rdp", "vnc", "sftp", "ftp", "ftps"] | None = None
    ip: str | None = Field(default=None, min_length=1, max_length=512)
    port: int | None = Field(default=None, ge=1, le=65535)
    identity_ids: list[int] | None = None
    folder_id: int | None = Field(default=None, ge=1)
    organization_id: int | None = Field(default=None, ge=1)
    monitoring_enabled: bool | None = None
    icon: str | None = Field(default=None, max_length=256)
