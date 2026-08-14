# Tool Reference

`nexterm-mcp` 0.2.0 exposes 89 typed tools. Nexterm remains the authorization boundary; this adapter does not provide a raw HTTP escape hatch.

All write tools require `NEXTERM_MUTATIONS_ENABLED=true`. The MCP annotations mark read-only and destructive operations so clients and gateways can apply an additional policy boundary. Destructive means the operation can permanently delete data, restore state, or stop/shut down an external workload.

| Tool | Access | Destructive | Important inputs | Purpose |
|---|---|---:|---|---|
| `nexterm_status` | Read | No | - | Verify authenticated Nexterm API access and report adapter/service status without exposing credentials. |
| `nexterm_list_entries` | Read | No | - | List accessible Nexterm entries. |
| `nexterm_recent_entries` | Read | No | `limit` | List recently connected Nexterm entries. |
| `nexterm_get_entry` | Read | No | `entry_id` | Get one Nexterm entry by ID. |
| `nexterm_create_entry` | Write | No | `name`, `protocol`, `ip`, `port`, `keyboard_layout`, `monitoring_enabled`, `node_name`, `vmid`, `rdp_security`, `jump_host_ids`, `mac_address`, `wake_on_lan_enabled`, `wol_broadcast_address`, `identity_ids`, `folder_id`, `organization_id`, `icon`, `renderer` | Create a Nexterm server entry using typed connection fields. |
| `nexterm_update_entry` | Write | No | `entry_id`, `name`, `entry_type`, `protocol`, `ip`, `port`, `keyboard_layout`, `monitoring_enabled`, `node_name`, `vmid`, `rdp_security`, `jump_host_ids`, `mac_address`, `wake_on_lan_enabled`, `wol_broadcast_address`, `identity_ids`, `folder_id`, `organization_id`, `icon`, `renderer` | Update typed fields on an entry while preserving unmodified Nexterm config fields. |
| `nexterm_delete_entry` | Write | Yes | `entry_id` | Permanently delete a Nexterm entry. |
| `nexterm_duplicate_entry` | Write | No | `entry_id` | Duplicate an existing Nexterm entry. |
| `nexterm_import_ssh_config` | Write | No | `servers`, `folder_id` | Import a typed batch of SSH server definitions into a Nexterm folder. |
| `nexterm_reposition_entry` | Write | No | `entry_id`, `placement`, `target_id`, `folder_id`, `organization_id` | Reposition or move a Nexterm entry. |
| `nexterm_wake_entry` | Write | No | `entry_id` | Send Wake-on-LAN for an entry using its configured WOL settings. |
| `nexterm_list_identities` | Read | No | - | List accessible Nexterm identity metadata. Credential material is never returned. |
| `nexterm_list_folders` | Read | No | - | List accessible Nexterm folders. |
| `nexterm_create_folder` | Write | No | `name`, `parent_id`, `organization_id` | Create a Nexterm folder. |
| `nexterm_update_folder` | Write | No | `folder_id`, `name`, `parent_id`, `organization_id` | Update or move a Nexterm folder. |
| `nexterm_delete_folder` | Write | Yes | `folder_id` | Permanently delete a Nexterm folder according to Nexterm's folder deletion semantics. |
| `nexterm_list_tags` | Read | No | - | List personal Nexterm tags. |
| `nexterm_create_tag` | Write | No | `name`, `color` | Create a Nexterm tag. |
| `nexterm_update_tag` | Write | No | `tag_id`, `name`, `color` | Update a Nexterm tag. |
| `nexterm_delete_tag` | Write | Yes | `tag_id` | Permanently delete a Nexterm tag. |
| `nexterm_assign_tag` | Write | No | `entry_id`, `tag_id` | Assign a tag to an entry. |
| `nexterm_unassign_tag` | Write | No | `entry_id`, `tag_id` | Remove a tag assignment from an entry. |
| `nexterm_list_entry_tags` | Read | No | `entry_id` | List tags assigned to an entry. |
| `nexterm_list_organizations` | Read | No | - | List organizations accessible to the configured Nexterm account. |
| `nexterm_get_organization` | Read | No | `organization_id` | Get organization details. |
| `nexterm_create_organization` | Write | No | `name`, `description` | Create a Nexterm organization. |
| `nexterm_update_organization` | Write | No | `organization_id`, `name`, `description` | Update organization name or description. |
| `nexterm_delete_organization` | Write | Yes | `organization_id` | Permanently delete a Nexterm organization. |
| `nexterm_list_organization_members` | Read | No | `organization_id` | List members of an organization. |
| `nexterm_get_organization_member_permissions` | Read | No | `organization_id`, `account_id` | Read one organization's effective member permissions. |
| `nexterm_get_organization_session_settings` | Read | No | `organization_id` | Read organization live-session settings. |
| `nexterm_update_organization_session_settings` | Write | No | `organization_id`, `enable_live_session_sharing` | Update organization live-session settings. |
| `nexterm_list_pending_invitations` | Read | No | - | List pending organization invitations for the configured account. |
| `nexterm_list_scripts` | Read | No | `search`, `organization_id` | List or search accessible scripts, optionally scoped to an organization. |
| `nexterm_list_all_scripts` | Read | No | - | List all accessible scripts across personal, organization and source scopes. |
| `nexterm_list_script_sources` | Read | No | - | List source-backed scripts. |
| `nexterm_get_script` | Read | No | `script_id`, `organization_id` | Get one script, optionally in an organization scope. |
| `nexterm_create_script` | Write | No | `name`, `content`, `description`, `organization_id`, `os_filter` | Create a Nexterm script. Script content is model-visible by design. |
| `nexterm_update_script` | Write | No | `script_id`, `organization_id`, `name`, `content`, `description`, `os_filter` | Update a Nexterm script. Script content is model-visible by design. |
| `nexterm_delete_script` | Write | Yes | `script_id`, `organization_id` | Permanently delete a Nexterm script. |
| `nexterm_reposition_script` | Write | No | `script_id`, `target_id`, `organization_id` | Reorder a Nexterm script relative to another script. |
| `nexterm_list_snippets` | Read | No | - | List all accessible Nexterm snippets. |
| `nexterm_list_snippet_sources` | Read | No | - | List source-backed snippets. |
| `nexterm_get_snippet` | Read | No | `snippet_id`, `organization_id` | Get one snippet, optionally in an organization scope. |
| `nexterm_create_snippet` | Write | No | `name`, `command`, `description`, `organization_id`, `os_filter` | Create a Nexterm command snippet. Command content is model-visible by design. |
| `nexterm_update_snippet` | Write | No | `snippet_id`, `organization_id`, `name`, `command`, `description`, `os_filter` | Update a Nexterm command snippet. |
| `nexterm_delete_snippet` | Write | Yes | `snippet_id`, `organization_id` | Permanently delete a Nexterm snippet. |
| `nexterm_reposition_snippet` | Write | No | `snippet_id`, `target_id`, `organization_id` | Reorder a Nexterm snippet relative to another snippet. |
| `nexterm_list_themes` | Read | No | - | List available Nexterm themes. |
| `nexterm_get_active_theme_css` | Read | No | - | Get CSS for the configured account's active theme. |
| `nexterm_get_theme` | Read | No | `theme_id` | Get theme metadata and content. |
| `nexterm_get_theme_css` | Read | No | `theme_id` | Get CSS for one theme. |
| `nexterm_create_theme` | Write | No | `name`, `css`, `description` | Create a custom Nexterm CSS theme. |
| `nexterm_update_theme` | Write | No | `theme_id`, `name`, `css`, `description` | Update a custom Nexterm CSS theme. |
| `nexterm_delete_theme` | Write | Yes | `theme_id` | Permanently delete a custom Nexterm theme. |
| `nexterm_set_active_theme` | Write | No | `theme_id` | Set an active theme, or pass null to clear the active theme. |
| `nexterm_list_sources` | Read | No | - | List configured Nexterm content sources. |
| `nexterm_get_source` | Read | No | `source_id` | Get one Nexterm content source. |
| `nexterm_validate_source` | Read | No | `url` | Validate a source URL and report discovered content counts. |
| `nexterm_create_source` | Write | No | `name`, `url` | Create and initially sync a Nexterm content source. |
| `nexterm_update_source` | Write | No | `source_id`, `name`, `url`, `enabled` | Update a Nexterm content source. |
| `nexterm_delete_source` | Write | Yes | `source_id` | Permanently delete a source and its synchronized content. |
| `nexterm_sync_source` | Write | No | `source_id` | Synchronize one Nexterm content source. |
| `nexterm_sync_all_sources` | Write | No | - | Trigger synchronization for all enabled content sources. |
| `nexterm_get_monitoring` | Read | No | - | Get current monitoring overview for accessible servers. |
| `nexterm_get_monitoring_settings` | Read | No | - | Get global Nexterm monitoring settings. |
| `nexterm_update_monitoring_settings` | Write | No | `status_checker_enabled`, `status_interval`, `monitoring_enabled`, `monitoring_interval`, `data_retention_hours`, `connection_timeout`, `batch_size` | Update global Nexterm monitoring settings. |
| `nexterm_get_integration_monitoring` | Read | No | `target_id`, `time_range` | Get monitoring history for an integration. |
| `nexterm_get_server_monitoring` | Read | No | `target_id`, `time_range` | Get monitoring history for a server entry. |
| `nexterm_get_audit_logs` | Read | No | `organization_id`, `action`, `resource`, `start_date`, `end_date`, `limit`, `offset` | Query Nexterm audit logs with bounded pagination and filters. |
| `nexterm_get_audit_metadata` | Read | No | - | Get available audit actions and resource metadata. |
| `nexterm_get_organization_audit_settings` | Read | No | `organization_id` | Get audit settings for an organization. |
| `nexterm_update_organization_audit_settings` | Write | No | `organization_id`, `require_connection_reason`, `enable_file_operation_audit`, `enable_server_connection_audit`, `enable_identity_management_audit`, `enable_identity_credentials_access_audit`, `enable_server_management_audit`, `enable_folder_management_audit`, `enable_script_execution_audit`, `enable_ai_operation_audit`, `enable_session_recording`, `recording_retention_days` | Update audit settings for an organization. |
| `nexterm_list_backup_files` | Read | No | `file_type` | List Nexterm recording or log files available to the backup subsystem. |
| `nexterm_delete_backup_file` | Write | Yes | `file_type`, `filename` | Permanently delete a Nexterm recording or log file. |
| `nexterm_get_backup_settings` | Read | No | - | Get backup settings and sanitized provider metadata. |
| `nexterm_update_backup_settings` | Write | No | `schedule_interval`, `retention`, `include_database`, `include_recordings`, `include_logs` | Update Nexterm backup schedule and inclusion settings. |
| `nexterm_get_backup_storage` | Read | No | - | Get Nexterm backup storage statistics. |
| `nexterm_delete_backup_provider` | Write | Yes | `provider_id` | Permanently delete a configured backup provider. Provider credential creation/update is intentionally not exposed. |
| `nexterm_list_provider_backups` | Read | No | `provider_id` | List backups stored by one configured provider. |
| `nexterm_create_backup` | Write | No | `provider_id` | Create a backup using an existing configured provider. |
| `nexterm_restore_backup` | Write | Yes | `provider_id`, `backup_name` | Restore a backup. Nexterm documents that this initiates a server restart. |
| `nexterm_get_integration` | Read | No | `integration_id` | Get sanitized metadata for one Nexterm integration. |
| `nexterm_delete_integration` | Write | Yes | `integration_id` | Permanently delete a Nexterm integration. |
| `nexterm_sync_integration` | Write | No | `integration_id` | Synchronize an existing Nexterm integration. |
| `nexterm_start_integration_entry` | Write | No | `entry_id` | Start the external resource represented by an integration entry. |
| `nexterm_stop_integration_entry` | Write | Yes | `entry_id` | Stop the external resource represented by an integration entry. |
| `nexterm_shutdown_integration_entry` | Write | Yes | `entry_id` | Request guest shutdown for the external resource represented by an integration entry. |
| `nexterm_list_engines` | Read | No | - | List Nexterm engine metadata. Token-bearing engine mutations are intentionally excluded. |

## Security and side effects

- The API key is file-backed and never accepted as a tool argument.
- Identity credential mutation, API-key management, raw HTTP, token-generating engine operations, interactive transports, and other credential-bearing API paths are intentionally excluded.
- Script, snippet, theme, and source content is application content and can be model-visible when returned by a tool.
- `nexterm_restore_backup` can initiate a Nexterm restart. Entry stop/shutdown tools affect the external resource represented by the integration entry.
- Create/update/sync operations are not classified as destructive, but they still change Nexterm state and require mutations to be enabled.

See [`SECURITY.md`](../SECURITY.md) for the complete credential and authorization boundary.
