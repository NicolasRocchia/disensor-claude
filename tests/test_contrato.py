"""The plugin's texts come from the pinned CLI, and the plugin stays skills-only.

A plugin that copied the runbook by hand would drift from the CLI it drives in
silence. These tests regenerate every text from the installed disensor and
compare it with what is committed. They need the pinned CLI on PATH and fail,
not skip, without it: a green run that checked nothing would be the drift
they exist to catch.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import generar  # noqa: E402

COMPONENT_KEYS = (
    "hooks", "mcpServers", "agents", "commands", "lspServers", "outputStyles",
    "workflows", "experimental", "channels", "skills",
)


def read(path: str) -> str:
    return (ROOT / path).read_bytes().decode("utf-8").replace(chr(13) + chr(10), chr(10))


def manifest() -> dict:
    return json.loads(read(".claude-plugin/plugin.json"))


def skill(name: str) -> str:
    return read(f"skills/{name}/SKILL.md")


def cli_or_fail() -> None:
    if shutil.which("disensor") is None:
        pytest.fail(f"disensor not on PATH: pip install disensor=={generar.PIN}")


def test_the_installed_cli_is_the_pinned_one():
    cli_or_fail()
    assert generar.installed_version() == generar.PIN


def test_the_generated_texts_match_what_is_committed():
    cli_or_fail()
    for path, text in generar.generate(generar.PIN).items():
        committed = path.read_bytes().decode("utf-8").replace(chr(13) + chr(10), chr(10))
        assert committed == text, f"{path.relative_to(ROOT)} drifted: run python tools/generar.py"


def test_every_copy_of_the_pin_is_the_same_version():
    """The pin lives in the generator; CI, the README and the setup skill repeat it."""
    assert manifest()["metadata"]["disensor"] == generar.PIN
    for path in (".github/workflows/ci.yml", "README.md", "skills/setup/SKILL.md"):
        found = set(re.findall(r"disensor==([0-9][^\s\"'`]*)", read(path)))
        assert found == {generar.PIN}, (path, found)
    assert "{{PIN}}" not in skill("setup")


def test_the_plugin_is_skills_only():
    """No executables, hooks, servers or agents, on disk or declared inline:
    chat and Cowork refuse a plugin with bin/, and hooks are code the plugin
    would run on every session."""
    for forbidden in ("bin", "hooks", ".mcp.json", ".lsp.json", "agents", "commands"):
        assert not (ROOT / forbidden).exists(), forbidden
    assert not (set(manifest()) & set(COMPONENT_KEYS)), "component declared in plugin.json"
    market = json.loads(read(".claude-plugin/marketplace.json"))
    for entry in market["plugins"]:
        assert not (set(entry) & set(COMPONENT_KEYS)), "component declared in the marketplace entry"
    for name in ("setup", "round"):
        frontmatter = skill(name).split("---")[1]
        assert "hooks:" not in frontmatter, f"{name}: hooks in the skill frontmatter"


def test_the_runbook_does_not_fetch_instructions_at_run_time():
    """The filling guide travels inside the skill: a plugin must not send Claude
    to pull behavioural instructions from an external source. The CLI's own
    pointer to `disensor guide` is rewritten in the runbook, and the guide
    reference carries the filling guide alone, not a second copy of the runbook."""
    flat = " ".join(skill("round").split())
    assert "`disensor guide` explains" not in flat
    assert "references/guide.md" in flat
    guide = " ".join(read("skills/round/references/guide.md").split())
    assert "`disensor guide` explains" not in guide
    assert "# Running a review event" not in guide


def test_the_round_is_invoked_by_the_user_only():
    assert "disable-model-invocation: true" in skill("round").split("---")[1]


def test_the_skills_leave_the_consent_to_the_owner():
    for name in ("setup", "round"):
        text = " ".join(skill(name).split()).lower()
        assert "reviewer consent" in text
        assert "never run" in text
