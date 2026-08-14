from pathlib import Path
import re

from nexterm_mcp.operations import OPERATIONS

ROOT = Path(__file__).resolve().parents[1]


def test_public_tool_reference_matches_server_contract() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    tools_doc = (ROOT / "docs" / "tools.md").read_text(encoding="utf-8")

    assert "docs/tools.md" in readme
    documented = set(re.findall(r"^\| `([^`]+)` \|", tools_doc, flags=re.MULTILINE))
    expected = {"nexterm_status", *(operation.name for operation in OPERATIONS)}
    assert documented == expected
