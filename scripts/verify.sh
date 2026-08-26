#!/usr/bin/env bash
set -euo pipefail
command -v docker >/dev/null 2>&1 || { echo "docker is required" >&2; exit 1; }
UV_IMAGE="${UV_IMAGE:-ghcr.io/astral-sh/uv:0.12.4-python3.12-trixie-slim}"
exec docker run --rm \
  -v "$PWD:/work" \
  -v /work/.venv \
  -v /root/.cache/uv \
  -w /work \
  "$UV_IMAGE" \
  bash -lc 'set -euo pipefail; work="$(mktemp -d)"; trap '\''rm -rf "$work"'\'' EXIT; uv sync --frozen --extra test; uv run --frozen python - <<'\''PY'\''
import importlib.metadata, tomllib
project=tomllib.load(open("pyproject.toml","rb"))["project"]["version"]
installed=importlib.metadata.version("nexterm-mcp")
assert installed == project, (installed, project)
PY
uv run --frozen pytest; uv build --wheel --out-dir "$work/dist"; test -n "$(find "$work/dist" -maxdepth 1 -type f -name "*.whl" -print -quit)"'
git diff --check
