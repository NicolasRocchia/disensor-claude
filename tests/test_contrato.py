"""The plugin's texts come from the pinned CLI, and the plugin stays skills-only.

A plugin that copied the runbook by hand would drift from the CLI it drives in
silence. These tests regenerate every text from the installed disensor and
compare it with what is committed; the install in CI is the pinned version, so
a release of the CLI that changes the runbook fails here before the plugin
ships it.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import generar  # noqa: E402

needs_cli = pytest.mark.skipif(
    shutil.which("disensor") is None,
    reason=f"disensor not on PATH: pip install disensor=={generar.PIN}",
)


def manifest() -> dict:
    return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))


def skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


@needs_cli
def test_the_installed_cli_is_the_pinned_one():
    assert generar.installed_version() == generar.PIN


@needs_cli
def test_the_generated_texts_match_what_is_committed():
    for path, text in generar.generate(generar.PIN).items():
        committed = path.read_bytes().decode("utf-8")
        assert committed == text, f"{path.relative_to(ROOT)} drifted: run python tools/generar.py"


def test_the_manifest_pins_the_same_version():
    assert manifest()["metadata"]["disensor"] == generar.PIN


def test_the_setup_skill_names_the_pin():
    text = skill("setup")
    assert f"disensor=={generar.PIN}" in text
    assert "{{PIN}}" not in text


def test_the_plugin_is_skills_only():
    """No executables, hooks or MCP servers: chat and Cowork refuse a plugin with
    bin/, and hooks are code the plugin would run on every session."""
    for forbidden in ("bin", "hooks", ".mcp.json", "agents", "commands"):
        assert not (ROOT / forbidden).exists(), forbidden


def test_the_runbook_does_not_fetch_instructions_at_run_time():
    """The filling guide travels inside the skill: a plugin must not send Claude
    to pull behavioural instructions from an external source. The CLI's own
    pointer to `disensor guide` is rewritten by the generator."""
    text = skill("round")
    assert "`disensor guide` explains" not in text
    assert "references/guide.md" in text
    assert (ROOT / "skills" / "round" / "references" / "guide.md").exists()


def test_the_skills_leave_the_consent_to_the_owner():
    for name in ("setup", "round"):
        # Sin saltos de linea: el texto viene cortado a 80 columnas.
        text = " ".join(skill(name).split()).lower()
        assert "reviewer consent" in text
        assert "never run" in text
