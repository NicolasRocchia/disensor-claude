---
name: setup
description: Set up disensor in the current repository with the disensor CLI pinned to 0.14.0. Use when the user asks to install, set up or configure disensor.
---

# Setting up disensor

Everything here runs on the user's machine through the `disensor` CLI, a
Python package on PyPI. This plugin installs nothing by itself: show every
command before running it, and run the ones that install software only after
the user agrees to that exact command.

## 1. Check which CLI the shell resolves

Run `disensor --version`.

- It prints `disensor 0.14.0`: go to step 2.
- It prints another version, or nothing: this plugin was written for 0.14.0.
  Propose `pipx install --force disensor==0.14.0` (`pipx install
  disensor==0.14.0` when it is not installed at all) and run it only after
  the user agrees. pipx installs from the index pip is configured to use,
  PyPI unless this machine overrides it: if `pip config list` or the
  environment (`PIP_INDEX_URL`, `PIP_EXTRA_INDEX_URL`) names another index,
  say so and let the user decide before installing. Never install another
  version or another package.
- After installing, run `disensor --version` again. If the shell still
  resolves another copy, an older `disensor` comes first on PATH: show where
  each one is (`which -a disensor`; on Windows `where.exe disensor`, or
  `Get-Command disensor -All` in PowerShell, where `where` alone is an alias
  of `Where-Object`) and stop until the user sorts it out. Every later
  command uses whatever the shell resolves, so this check is the one that
  matters.

The CLI needs Python 3.10 or newer and `pipx`. If `pipx` is missing, say so
and propose the install pipx documents for the platform, run from the user's
home directory and not from the repository: `brew install pipx` on macOS,
`py -m pip install --user pipx` on Windows, the distribution package or
`python3 -m pip install --user pipx` on Linux; then `pipx ensurepath`. The
home directory matters because `python -m` looks in the current directory
first, so a repository can carry a `pip.py` or `pipx.py` that would run
instead. `ensurepath` changes PATH for new shells only: the user opens a new
terminal, starts Claude Code there, and comes back to step 1 so the CLI gets
installed and checked. If the machine has no Python 3.10 or newer, stop and
say what is missing; do not install Python.

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
`disensor init --upgrade --no-claude` to bring the gate to 0.14.0. With
network it resolves tag `v0.14.0` and pins the `uses:` line to that commit,
also when the line was left on the tag; without network it leaves the
workflow as it is and prints a WARNING that sends to `disensor pin`. Then
read the `uses:` line of that workflow: it has to end in a 40-character
commit SHA, because a tag can be moved. If it still says `@v0.14.0`, or
`--upgrade` warned, run `disensor pin` when there is network.

To try disensor without touching CI, `disensor init --no-claude --no-workflow`
does the same without the workflow. The workflow runs the gate on every pull
request; making it a required check is a branch protection setting on the
hosting side, which disensor's README describes under deployment
requirements.

## 3. Find a reviewer

Run `disensor reviewer suggest`. It is offline: it reports which catalogued
reviewer CLIs this machine has, with the notes of each recipe it found: what
the catalogue knows about how that reviewer is confined and what is still
unverified. Relay those notes as printed. `verified` for `codex` holds only
on the platform and codex-cli version pairs its hostile test ran on (with
0.14.0, 0.153.4 and 0.162.1 on Windows); with any other, the round records
the version and the declaration carries `unverified` and its item. That is
the round's to find out, not yours to test. The reviewer has to come from a
model family other than the one writing the code; that is the point of the
round.

Register one from the catalogue with `disensor reviewer add <id>`; `codex`
and `ollama` need `--model <the model the account runs>`. For a reviewer that
sends material out of the machine, `add` prints the entry and exits with 2
asking for `--yes`: show the user what it printed, and either they re-run it
with `--yes` or you add `--yes` only after they say so for that exact entry.
Then `disensor reviewer list` shows what was registered.

The `codex` recipe runs from an isolated `CODEX_HOME`
(`~/.disensor/reviewers/codex/home`, policy `codex_home/1`) with nothing of
the user's own codex configuration in it, so that home needs its own
credentials: `disensor reviewer login codex`, once per machine. The owner
runs it from their terminal, because it signs the home in with their account
(the browser flow, or `--device-auth`; `--with-api-key` reads a key from
standard input). Never run it yourself: show the command and say why it is
theirs. disensor never reads, copies or stores those credentials. To know
whether the home is signed in, `disensor reviewer login codex --status`
only asks the CLI, and that one you can run. A `codex` entry whose home was
never signed in ends its attempt in `not_authenticated`, and the round moves
on to the next reviewer or exits with 4 when there is none.

A catalogue entry keeps the command and the isolation policy of the day it
was registered: when a later disensor changes that recipe, as `claude` did
when it gained `--safe-mode` and `codex` did when it moved into the isolated
home in 0.14.0, the round leaves the entry out and says to remove it and add
it again; `list` does not flag it. Propose that like any other `add`:
`disensor reviewer remove codex`, then `disensor reviewer add codex --model
<model> --yes` once the user approved that entry, then the owner's `login`,
and the owner's `disensor reviewer consent codex` again in every repository
that runs rounds, because the consent covers the recipe that changed.

An entry outside the catalogue is an executable that will later receive the
material under review. Do not run a candidate to inspect it, not even with
`--help`: propose it, show exactly what `reviewer add` prints, and let the
owner approve it; never pass `--yes` for them.

The catalogue marks `ollama` as a reviewer that keeps everything on the
machine, and the CLI asks for no consent for it. That is true only when the
Ollama server runs on this machine and the model is a downloaded one: Ollama
also serves cloud models (names ending in `:cloud`), whose prompts go to
Ollama's servers, and `OLLAMA_HOST` can point the client at a server
elsewhere. Before registering `ollama`, check the model name and whether
`OLLAMA_HOST` is set; if either sends the material out, say so and let the
user choose.

## 4. Stop at the consent

Sending the repository's material to a cloud reviewer needs
`disensor reviewer consent <id>`, run by the owner of the repository, once per
repository, recipe and executable. Never run it yourself, not even after the
user approved the round in the chat: tell them the command and why it is
theirs to run. A consent given to the `codex` entry of an earlier disensor
does not carry over to the one registered with 0.14.0, because the recipe
changed: the owner gives it again. `disensor reviewer login codex` is the
owner's for the same reason: it signs the isolated home in with their
account.

## 5. Report

Say what was installed and which `disensor` the shell resolves, what `init`
wrote or kept, which reviewer is registered and, when it has an isolated
home, whether it is signed in, and what is still the owner's to do: the
`login`, the `consent`, or both. The round is `/disensor:round`, and the
user invokes it.
