# nexterm-mcp

A deliberately bounded Model Context Protocol server for managing [Nexterm](https://github.com/gnmyt/Nexterm) through its supported REST API.

This community project is not affiliated with or endorsed by the Nexterm project.

## Why this exists

Nexterm exposes a broad authenticated API. Agent workflows usually need a much smaller surface: inspect existing entries, folders and identity metadata, then create or update selected server entries without exposing credentials or arbitrary API access.

`nexterm-mcp` intentionally provides that smaller boundary:

- entry discovery and detail reads;
- folder and identity metadata discovery;
- bounded entry create, update and delete operations;
- API-key authentication from a private file;
- mutations disabled by default;
- defensive credential-field removal from API responses;
- no generic HTTP/request tool;
- no identity credential retrieval or identity mutation;
- no Nexterm API-key management.

The initial contract is tested against Nexterm `v1.2.2-BETA` API routes.

## Tool surface

| Tool | Behavior |
|---|---|
| `nexterm_status` | Verify authenticated API access and report adapter status. |
| `nexterm_list_entries` | List accessible entries. |
| `nexterm_get_entry` | Read one entry by ID. |
| `nexterm_list_identities` | List identity metadata for selecting existing identity IDs. |
| `nexterm_list_folders` | List folders for selecting existing folder IDs. |
| `nexterm_create_entry` | Create a server entry using supported bounded fields. |
| `nexterm_update_entry` | Update supported fields on an existing entry. |
| `nexterm_delete_entry` | Permanently delete an entry. |

The last three tools fail closed unless mutations are enabled in the MCP server environment.

## Requirements

- Python 3.12+
- Nexterm with API-key support (`v1.2.2-BETA` or a compatible newer release)
- An MCP client that supports stdio servers

## Configuration

| Variable | Required | Default | Meaning |
|---|---:|---|---|
| `NEXTERM_BASE_URL` | yes | - | Nexterm base URL, for example `https://nexterm.example.com`. |
| `NEXTERM_API_KEY_FILE` | yes | - | Absolute path to a mode-`0600` file containing the Nexterm API key. |
| `NEXTERM_TIMEOUT_SECONDS` | no | `15` | HTTP timeout, maximum 120 seconds. |
| `NEXTERM_MUTATIONS_ENABLED` | no | `false` | Enables entry create/update/delete tools when set to `true`. |

Example MCP registration:

```json
{
  "mcpServers": {
    "nexterm": {
      "command": "nexterm-mcp",
      "env": {
        "NEXTERM_BASE_URL": "https://nexterm.example.com",
        "NEXTERM_API_KEY_FILE": "/run/secrets/nexterm-api-key",
        "NEXTERM_MUTATIONS_ENABLED": "false"
      }
    }
  }
}
```

## Entry model

Create and update tools expose a stable subset of Nexterm's server-entry fields:

- `name`
- `protocol`: `ssh`, `telnet`, `rdp`, `vnc`, `sftp`, `ftp`, `ftps`
- `ip`
- `port`
- `identity_ids`
- `folder_id`
- `organization_id`
- `monitoring_enabled`
- `icon`

The MCP adapter translates these fields to Nexterm's API payload shape. It does not expose an arbitrary `config` object.

## Development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest
```

## Security

See [SECURITY.md](SECURITY.md). In particular, keep mutation tools behind an administrative MCP policy boundary and treat the Nexterm API key as an administrative credential according to the permissions of its account.

## License

MIT
