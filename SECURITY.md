# Security Policy

## Security model

`nexterm-mcp` exposes broad typed Nexterm management without providing a generic API escape hatch.

- Use a dedicated Nexterm API key where practical.
- The API key is read from `NEXTERM_API_KEY_FILE`; it is never accepted as an MCP tool argument or returned as output.
- The API key file must be a regular non-symlink file with no group or other permissions.
- There is no generic HTTP or arbitrary Nexterm API request tool.
- Read responses are defensively stripped of common credential-shaped fields such as passwords, passphrases, private keys, API keys, access/refresh tokens, authorization values and credential objects.
- HTTP error response bodies are not echoed into MCP errors.
- All non-read-only tools are disabled by default and require `NEXTERM_MUTATIONS_ENABLED=true` in the MCP server environment.
- Destructive or disruptive delete, restore, stop and shutdown tools are marked destructive in their MCP annotations.

A Nexterm API key acts with the authorization of its linked Nexterm account. Nexterm `v1.2.2-BETA` API keys do not provide an independent per-key scope in the API contract used by this project, so protect the MCP host and use the narrowest practical Nexterm account permissions.

## Credential-bearing API exclusions

Some supported Nexterm REST endpoints deliberately have no MCP tool because their normal request or response contract contains credential material:

- identity create/update/delete/move;
- Nexterm API-key management;
- Proxmox integration create/update, which accepts a plaintext password;
- backup-provider create/update, which may accept a plaintext password;
- engine registration and token regeneration, which can issue engine tokens;
- account password, TOTP and passkey management.

Do not work around these exclusions by adding a raw HTTP tool or by passing passwords, private keys, passphrases or generated tokens as ordinary model-visible MCP arguments. If future versions support these operations, credential values should enter or leave through a non-model-visible mechanism such as narrowly approved private files.

## Other high-impact operations

The public server also exposes operations that do not carry credentials but can materially alter state when mutations are enabled. Examples include deleting resources, deleting backup files/providers, restoring a backup, and stopping or shutting down an integration-backed workload.

MCP clients and gateways should apply their own policy boundary. A typical deployment should expose read tools broadly only when needed and keep mutation tools on an administrative surface.

Scripts, snippets and theme/source content are application content rather than credential fields. Their bodies are intentionally returned by the corresponding MCP tools and may therefore be visible to the model. Do not store secrets in those resources if model visibility is unacceptable.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/X1pheR/nexterm-mcp/security/advisories/new) for sensitive reports. If that form is unexpectedly unavailable, open a public issue only to request a private contact route and include no exploit details, credentials, tokens, private keys or other sensitive material.

## Dependency and code security

The repository uses locked Python dependencies, full-SHA-pinned GitHub Actions, frozen CI/package verification, Dependabot and OpenSSF Scorecard. Public-release acceptance also requires applicable GitHub-native dependency alerts, secret scanning with push protection and CodeQL code scanning to be reviewed and green before a release is published.

These scanners supplement rather than replace source/history review and the project test suite.
