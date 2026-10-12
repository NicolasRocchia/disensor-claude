---
name: setup
description: Set up disensor in the current repository with the disensor CLI pinned to 0.12.1. Use when the user asks to install, set up or configure disensor, or when a disensor command is not found.
---

# Setting up disensor

Everything here runs on the user's machine through the `disensor` CLI, a
Python package on PyPI. This plugin installs nothing by itself: every command
below is shown to the user before it runs, and the ones that install software
or send material anywhere wait for their approval.

## 1. Check the CLI

Run `disensor --version`.

- It prints `disensor 0.12.1`: go to step 2.
- It prints another version: tell the user this plugin was written for
  0.12.1 and propose `pipx install --force disensor==0.12.1`. Run it only
  after they agree.
- The command is not found: propose `pipx install disensor==0.12.1` and run
  it only after they agree. If `pipx` itself is missing, say so and show
  `python -m pip install --user pipx` followed by `python -m pipx ensurepath`;
  do not improvise another way to install. Never install a different version,
  a different package, or anything from a source other than PyPI.

## 2. Scaffold the repository

From the repository root, run `disensor init --no-claude`. It writes
`disensor.config.json` (the criticality level, versioned with the code), the
CI gate workflow pinned to the commit of the release tag, and a `.gitignore`
line for the report the gate writes. `--no-claude` is deliberate: this plugin
already carries the runbook, so the CLI does not write its own CLAUDE.md
section or repository skill.

If the report says the tag could not be resolved, run `disensor pin` when
there is network. If the repository already has `.claude/skills/disensor/`
from an earlier `disensor init`, say that it duplicates this plugin's runbook
and let the user decide whether to remove it; do not remove it yourself.

To try disensor without touching CI, `disensor init --no-claude --no-workflow`
does the same without the workflow.

## 3. Find a reviewer

Run `disensor reviewer suggest`. It is offline: it reports which catalogued
reviewer CLIs this machine has. Register one from the catalogue with
`disensor reviewer add <id>` (`codex` needs `--model <the model the account
runs>`). The reviewer has to come from a model family other than the one
writing the code: that is the point of the round.

An entry outside the catalogue is an executable that will later receive the
material under review. Propose it, show exactly what `reviewer add` prints,
and let the owner approve it; never pass `--yes` for them.

## 4. Stop at the consent

Sending the repository's material to a cloud reviewer needs
`disensor reviewer consent <id>`, run by the owner of the repository. Never
run it yourself, not even after the user approved the round in the chat: tell
them the command and why it is theirs to run. A local reviewer (`ollama`)
needs no consent.

## 5. Report

Say what was installed, what `init` wrote or kept, which reviewer is
registered, and what is still the owner's to do. Then the round is
`/disensor:round`.
