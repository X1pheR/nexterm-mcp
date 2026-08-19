# Changelog

This file records user-visible changes to `nexterm-mcp`. Security fixes with a public CVE or equivalent identifier are called out explicitly in the release that fixes them.

## Unreleased

- Added public OpenSSF Scorecard reporting and protected-branch repository controls.
- Future releases publish signed GitHub/Sigstore build provenance alongside checksums and reproducible wheel artifacts.
- Added explicit contribution and private vulnerability-reporting routes.

## 0.2.0 - 2026-08-14

- Expanded the typed Nexterm surface to 89 tools across entries, folders, organizations, scripts, snippets, themes, sources, monitoring, audit, backup and bounded integration administration.
- Preserved the deliberate credential-bearing and authentication/authorization exclusions rather than adding generic request escape hatches.
- Added mutation-default-off behavior and destructive annotations for disruptive operations.
- Published the reproducible wheel with `SHA256SUMS` and documented Nexterm `v1.2.2-BETA` as the tested API contract baseline.

## 0.1.0

- Initial typed Nexterm MCP release focused on entry, folder and identity workflows.
