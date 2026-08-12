# Security Policy

## Security model

`nexterm-mcp` is intentionally narrower than a general Nexterm API client.

- Use a dedicated Nexterm API key where practical.
- The API key is read from `NEXTERM_API_KEY_FILE`; it is never accepted as an MCP tool argument or returned as output.
- The API key file must be a regular non-symlink file with no group or other permissions.
- There is no generic HTTP or arbitrary Nexterm API request tool.
- Read responses are defensively stripped of common credential-shaped fields such as passwords, passphrases, private keys, API keys, tokens and secrets.
- Entry mutations are disabled by default and require `NEXTERM_MUTATIONS_ENABLED=true` in the MCP server environment.
- This server does not create, edit, delete or reveal Nexterm identities or API keys.
- Gateway or MCP-client policy should keep mutation tools away from read-only consumers.

A Nexterm API key acts with the authority granted to its Nexterm account. Protect the MCP host and configure that Nexterm account with only the permissions required for the intended workflow.

## Reporting a vulnerability

Use GitHub private vulnerability reporting when available. Do not open a public issue containing API keys, passwords, private keys or other credentials.
