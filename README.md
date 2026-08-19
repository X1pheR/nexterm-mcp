# nexterm-mcp

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/X1pheR/nexterm-mcp/badge)](https://scorecard.dev/viewer/?uri=github.com/X1pheR/nexterm-mcp)

A typed Model Context Protocol server for broad management of [Nexterm](https://github.com/gnmyt/Nexterm) through its supported REST API.

This community project is not affiliated with or endorsed by the Nexterm project.

## Design

`nexterm-mcp` maps Nexterm resources and actions to explicit MCP tools instead of exposing a generic HTTP request primitive. This keeps tool inputs discoverable, validates common fields before a request is sent, provides MCP read/destructive annotations, and keeps the Nexterm API key outside model-visible arguments.

Version `0.2.0` provides 89 MCP tools and is contract-tested against Nexterm `v1.2.2-BETA` routes. The original `0.1.0` entry/folder/identity tool names remain available. See the complete [`docs/tools.md`](docs/tools.md) reference for access classification, destructive semantics, inputs and purpose.

The adapter intentionally does **not** mirror every Nexterm endpoint. Endpoints that require plaintext credential material, return newly generated credentials, mutate authentication/authorization, or represent interactive transports are excluded rather than weakened into an unsafe generic tool.

## Coverage

| Area | Coverage | Notes |
|---|---|---|
| Service/account status | Supported | `nexterm_status` verifies API-key authentication through `/api/accounts/me` and reads the service version. |
| Entries | Broad | List, recent, get, create, update, delete, duplicate, typed SSH import, reposition and Wake-on-LAN. |
| Folders | Full resource CRUD | List, create, update/move and delete. |
| Identities | Metadata read only | Credential-bearing identity create/update/delete/move is intentionally excluded. |
| Tags | Full | List, CRUD, assign/unassign and per-entry tag discovery. |
| Organizations | Resource/settings + read | List/get/CRUD, member reads, member-permission reads and session settings. Membership and permission mutations are excluded. |
| Scripts | Broad | List/search, all/source discovery, get, CRUD and reposition. Script content is model-visible. |
| Snippets | Broad | List/source discovery, get, CRUD and reposition. Command content is model-visible. |
| Themes | Full resource management | List/get/CSS, CRUD and active-theme selection. |
| Sources | Full | List/get/validate/CRUD and synchronization actions. |
| Monitoring | Full | Overview, global settings and server/integration history for Nexterm's `1h`, `6h` and `24h` ranges. |
| Audit | Broad | Log query, metadata and organization audit settings. Binary recording download is excluded. |
| Backup | Broad safe subset | File listing/deletion, settings, storage, provider deletion, backup listing/create/restore. Provider create/update is excluded because it accepts plaintext passwords. |
| Proxmox integrations | Safe subset | Read, delete, sync and entry start/stop/shutdown. Create/update is excluded because Nexterm requires a plaintext password. |
| Engines | Metadata read only | Token-generating create/regenerate operations are intentionally excluded. |

### Explicit exclusions

The following Nexterm API areas are not exposed as normal MCP tools in `0.2.0`:

- generic/raw HTTP or arbitrary Nexterm API requests;
- Nexterm API-key management;
- account password, TOTP, passkey and authentication-provider management;
- user and permission administration;
- organization invitations, member removal, permission mutation, invitation response and leave actions;
- identity credential create/update/delete/move;
- Proxmox integration create/update because the API requires a plaintext password;
- backup-provider create/update because the API may require a plaintext password;
- engine registration/token generation or token regeneration;
- audit recording binary download;
- interactive terminal, connection, SFTP, WebSocket, share and session transports;
- Nexterm AI operations.

These are security or protocol boundaries, not missing raw escape hatches. A future credential-mutating tool should use a non-model-visible delivery mechanism such as private local files rather than accepting passwords or private keys as MCP arguments.

## Security defaults

- The API key is read from a private local file and never accepted as a tool argument.
- API-key files must be regular non-symlink files with no group or other permissions.
- Common credential-shaped response fields are removed recursively before MCP output is returned.
- HTTP error bodies are not echoed into MCP errors.
- All mutation tools fail closed unless `NEXTERM_MUTATIONS_ENABLED=true`.
- Delete, restore, stop and shutdown operations that can cause irreversible or disruptive effects are marked destructive in MCP annotations.
- There is no raw request tool.

See [SECURITY.md](SECURITY.md) for the full security model.

## Feedback and contributions

Use [GitHub Issues](https://github.com/X1pheR/nexterm-mcp/issues) for bug reports and feature requests and pull requests for proposed changes. See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow, test requirements, and change expectations. Security issues must follow the private process in [SECURITY.md](SECURITY.md).

User-visible release changes are summarized in [CHANGELOG.md](CHANGELOG.md).

## Requirements

- Python 3.12+
- Nexterm with API-key support (`v1.2.2-BETA` or a compatible newer release)
- An MCP client that supports stdio servers

## Configuration

| Variable | Required | Default | Meaning |
|---|---:|---|---|
| `NEXTERM_BASE_URL` | yes | - | Nexterm base URL, for example `https://nexterm.example.com`. |
| `NEXTERM_API_KEY_FILE` | yes | - | Absolute path to a private mode-`0600` file containing the Nexterm API key. |
| `NEXTERM_TIMEOUT_SECONDS` | no | `15` | HTTP timeout, maximum 120 seconds. |
| `NEXTERM_MUTATIONS_ENABLED` | no | `false` | Enables all non-read-only tools when set to `true`. |

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

Use an MCP gateway or client-side allowlist when a consumer only needs a subset of the 89 tools. In particular, keep mutations and administrative reads away from consumers that only need entry discovery.

## Running a release

Accepted releases publish a reproducible wheel and `SHA256SUMS`. For `v0.2.0`:

```bash
uvx --python 3.12 \
  --from https://github.com/X1pheR/nexterm-mcp/releases/download/v0.2.0/nexterm_mcp-0.2.0-py3-none-any.whl \
  nexterm-mcp
```

Provide the same environment variables shown above. Release tags are the stable source snapshot; the wheel is the runtime artifact.

## Running from source

The repository includes `uv.lock` so source deployments can use a reproducible dependency set without installing the package globally.

```bash
uv sync --frozen
NEXTERM_BASE_URL=https://nexterm.example.com \
NEXTERM_API_KEY_FILE=/run/secrets/nexterm-api-key \
uv run --frozen nexterm-mcp
```

Mutations remain disabled in this example. Set `NEXTERM_MUTATIONS_ENABLED=true` only on an MCP surface where state-changing Nexterm tools are intentionally permitted.

A stdio gateway can launch the checkout directly as well:

```json
{
  "command": "uv",
  "args": ["run", "--frozen", "--directory", "/path/to/nexterm-mcp", "nexterm-mcp"],
  "env": {
    "NEXTERM_BASE_URL": "https://nexterm.example.com",
    "NEXTERM_API_KEY_FILE": "/run/secrets/nexterm-api-key",
    "NEXTERM_MUTATIONS_ENABLED": "false"
  }
}
```

## Entry model

Entry create/update uses typed connection fields rather than an arbitrary `config` object; the exact inputs are listed in [`docs/tools.md`](docs/tools.md). Partial updates first read the current entry and merge only requested connection fields into the existing Nexterm `config` object. This preserves fields that a compatible Nexterm release may already store but that the caller did not ask to change.

## Compatibility

The API contract currently follows Nexterm `v1.2.2-BETA`. Nexterm is still evolving, so a newer release may add or change routes or validation fields. `nexterm_status` reports the server version returned by Nexterm, while tests pin the adapter's known route contract.

The adapter deliberately relies on Nexterm's own authorization checks. A Nexterm API key acts with the permissions of its linked Nexterm account; the MCP server does not invent a second authorization model.

## Development

With `uv`:

```bash
uv sync --frozen --extra test
uv run --frozen --extra test pytest
```

A conventional virtual environment remains supported:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest
```

Build a wheel with:

```bash
uv build
```

GitHub CI uses the frozen dependency set for package-version verification, tests and wheel builds. Dependabot maintains locked dependencies and pinned workflow dependencies within accepted compatibility ranges. OpenSSF Scorecard runs on `main` and weekly and publishes its public result for independent repository-security review.

Normal development does not publish a release. An accepted strict SemVer tag (`vMAJOR.MINOR.PATCH`) triggers the release workflow, which verifies the exact tag/source/package version, reruns frozen tests, proves two independent wheel builds are byte-identical, generates signed GitHub/Sigstore build provenance, creates a draft release, attaches the wheel, `SHA256SUMS` and provenance bundle, and only then publishes the release.

## License

MIT
