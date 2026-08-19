# Contributing

Contributions are welcome through GitHub issues and pull requests.

## Before opening a change

- Use GitHub Issues for reproducible bugs and feature proposals.
- Use the private reporting process in [SECURITY.md](SECURITY.md) for suspected vulnerabilities or secret-handling defects.
- Keep a pull request focused on one coherent change and avoid unrelated formatting or dependency churn.
- Never include production Nexterm API keys, passwords, private keys, passphrases, generated tokens, private endpoints, or other credentials in issues, fixtures, tests, logs, or commits.

## Development setup

Use Python 3.12 and the committed lock file:

```bash
uv sync --frozen --extra test
uv run --frozen pytest
uv build --wheel
```

## Change requirements

- Add or update automated tests for new behavior and bug fixes where a regression test is practical.
- Preserve the typed MCP surface and credential exclusions; do not add a generic HTTP or secret-reveal escape hatch.
- Update `docs/tools.md` when a tool, mutation classification, input/output contract, guard, or permission requirement changes.
- Update README or security documentation when requirements, compatibility, configuration, or trust boundaries change.
- Add a concise entry under `Unreleased` in [CHANGELOG.md](CHANGELOG.md) for user-visible changes.
- Keep dependency changes within declared compatibility bounds unless the pull request explicitly owns a compatibility change.

A pull request is ready for review when frozen tests and the wheel build pass and its documentation describes the behavior it changes.
