---
name: setup
description: Set up disensor in the current repository with the disensor CLI pinned to {{PIN}}. Use when the user asks to install, set up or configure disensor.
---

# Setting up disensor

Everything here runs on the user's machine through the `disensor` CLI, a
Python package on PyPI. This plugin installs nothing by itself: show every
command before running it, and run the ones that install software only after
the user agrees to that exact command.

## 1. Check which CLI the shell resolves

Run `disensor --version`.

- It prints `disensor {{PIN}}`: go to step 2.
- It prints another version, or nothing: this plugin was written for {{PIN}}.
  Propose `pipx install --force disensor=={{PIN}}` (`pipx install
  disensor=={{PIN}}` when it is not installed at all) and run it only after
  the user agrees. pipx installs from the index pip is configured to use,
  PyPI unless this machine overrides it: if `pip config list` or the
  environment (`PIP_INDEX_URL`, `PIP_EXTRA_INDEX_URL`) names another index,
  say so and let the user decide before installing. Never install another
  version or another package.
- After installing, run `disensor --version` again. If the shell still
  resolves another copy, an older `disensor` comes first on PATH: show where
  each one is (`which -a disensor`, or `where disensor` on Windows) and stop
  until the user sorts it out. Every later command uses whatever the shell
  resolves, so this check is the one that matters.

If `pipx` is missing, say so and propose, from the user's home directory and
not from the repository, `python -I -m pip install --user pipx` and then
`python -m pipx ensurepath`. `python -m` looks in the current directory
first, so a repository can carry a `pip.py` or `pipx.py` that would run
instead; the home directory and `-I` avoid that. `ensurepath` changes PATH
for new shells only: after it, the user restarts Claude Code before step 2.
Do not improvise another way to install.

## 2. Scaffold the repository

From the repository root, run `disensor init --no-claude`. It writes
`disensor.config.json` (the criticality level, versioned with the code), the
CI gate workflow pinned to the commit of the release tag, and a `.gitignore`
line for the report the gate writes. `--no-claude` is deliberate: this plugin
carries the runbook, so the CLI does not write its own CLAUDE.md section or
repository skill.

What `init` keeps, it does not update. If the repository already has a
`## disensor` section in `CLAUDE.md` or a `.claude/skills/disensor/` directory
from an earlier `disensor init`, say so: that section may tell Claude to run
rounds on its own, which this plugin does not do, and that skill duplicates
this runbook. Let the user decide whether to remove them; do not remove them
yourself. If `.github/workflows/disensor.yml` already exists, run
`disensor init --upgrade --no-claude` so the gate is pinned to {{PIN}}; if the
report says a tag could not be resolved, run `disensor pin` when there is
network.

To try disensor without touching CI, `disensor init --no-claude --no-workflow`
does the same without the workflow. The workflow runs the gate on every pull
request; making it a required check is a branch protection setting on the
hosting side, which disensor's README describes under deployment
requirements.

## 3. Find a reviewer

Run `disensor reviewer suggest`. It is offline: it reports which catalogued
reviewer CLIs this machine has. The reviewer has to come from a model family
other than the one writing the code; that is the point of the round.

Register one from the catalogue with `disensor reviewer add <id>`; `codex`
and `ollama` need `--model <the model the account runs>`. For a reviewer that
sends material out of the machine, `add` prints the entry and exits with 2
asking for `--yes`: show the user what it printed, and either they re-run it
with `--yes` or you add `--yes` only after they say so for that exact entry.
Then `disensor reviewer list` shows what was registered.

An entry outside the catalogue is an executable that will later receive the
material under review. Do not run a candidate to inspect it, not even with
`--help`: propose it, show exactly what `reviewer add` prints, and let the
owner approve it; never pass `--yes` for them.

The catalogue marks `ollama` as a reviewer that keeps everything on the
machine, and the CLI asks for no consent for it. Ollama can also serve cloud
models (names ending in `:cloud`), whose prompts go to Ollama's servers: if the
user picks one of those, say that the material leaves the machine anyway and
let them choose.

## 4. Stop at the consent

Sending the repository's material to a cloud reviewer needs
`disensor reviewer consent <id>`, run by the owner of the repository, once per
repository, recipe and executable. Never run it yourself, not even after the
user approved the round in the chat: tell them the command and why it is
theirs to run.

## 5. Report

Say what was installed and which `disensor` the shell resolves, what `init`
wrote or kept, which reviewer is registered, and what is still the owner's to
do. The round is `/disensor:round`, and the user invokes it.
