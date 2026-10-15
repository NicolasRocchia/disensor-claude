# disensor for Claude

A Claude plugin that runs a cross-model adversarial review round with the
[disensor](https://github.com/NicolasRocchia/disensor) CLI and declares its
residue: the versioned record of what the review could not establish,
validated locally and enforced by a CI gate.

The plugin is two skills. `/disensor:setup` gets the CLI installed and the
repository scaffolded. `/disensor:round` runs the round against a reviewer
from another model family, has Claude verify every finding against the code,
and fills the declaration that goes into the pull request. Only you can start
a round: the skill is marked so that Claude does not load it on its own.

## Install

In Claude Code, from any session:

```
claude plugin install disensor --marketplace NicolasRocchia/disensor-claude
```

or, on versions before 2.1.292, in two steps:

```
/plugin marketplace add NicolasRocchia/disensor-claude
/plugin install disensor@disensor
```

In claude.ai or the Claude desktop app, open **Customize > Plugins > Add >
Add marketplace** and enter `NicolasRocchia/disensor-claude`. A plugin added
there also reaches Cowork and Claude Code on the same account.

## What it does on your machine

Everything happens through the `disensor` CLI, a Python package on PyPI. The
plugin itself bundles no executable, hook or server, and sends nothing
anywhere.

- `/disensor:setup` checks `disensor --version`. If the CLI is missing it
  proposes `pipx install disensor==0.14.0`, the exact version this plugin was
  written for, and runs it only after you approve. Then it runs
  `disensor init --no-claude` at the repository root, which writes
  `disensor.config.json`, the CI gate workflow and a `.gitignore` line, and
  `disensor reviewer suggest`, which reports offline which reviewer CLIs the
  machine has, with the notes of each recipe it found. The `codex` reviewer
  runs from an isolated `CODEX_HOME` under `~/.disensor` that you sign in
  once with `disensor reviewer login codex`; the skills never run that
  command for you either.
- `/disensor:round` runs `disensor round`, which packages the diff or the plan
  with the adversarial brief and hands it to the reviewer you registered. That
  reviewer's own CLI sends the material to its provider. For a reviewer the
  CLI classifies as cloud, that happens only after the repository owner ran
  `disensor reviewer consent` for that repository, that recipe and that
  executable; the skills never run that command for you. A reviewer that runs
  the model on your machine sends nothing. The CLI treats `ollama` as one and
  asks for no consent for it, but Ollama can also serve cloud models
  (`:cloud`) or talk to a server named by `OLLAMA_HOST`, so the setup skill
  checks both before registering it.
- The declaration lands in `.residue/` of your repository, in its own commit,
  and the gate validates it on the pull request. Making that check required
  for merging is a branch protection setting on your side; disensor's README
  lists it under deployment requirements.

The runbook in `skills/round/SKILL.md` and the filling guide in
`skills/round/references/guide.md` are generated from the pinned CLI
(`tools/generar.py`), not copied by hand. `tests/test_contrato.py` regenerates
them and fails on any drift.

## Where it works

The round needs a terminal with the CLI, so it runs in Claude Code. In
claude.ai chat and Cowork the skills load and can explain the method and the
declaration, but there is no `disensor` to run there.

## Privacy

disensor collects nothing. The only data that leaves your machine goes where
you send it: to the reviewer you registered and consented to, and to PyPI and
GitHub when you install or scaffold. The full statement is at
[disensor.dev/privacy](https://disensor.dev/privacy/).

## Development

```
pip install disensor==0.14.0 pytest
python tools/generar.py      # regenerate the skills from the pinned CLI
pytest -q                    # the contract: generated texts, pin, skills-only
claude plugin validate --strict .
claude --plugin-dir .        # try it in a session
```

To move to a new disensor release: change `PIN` in `tools/generar.py`,
install that version and regenerate. The tests name every other place that
carries the version (`plugin.json`, the CI workflow, this README) until they
all agree. Then raise the plugin `version`.

## Support and license

Issues: [github.com/NicolasRocchia/disensor-claude/issues](https://github.com/NicolasRocchia/disensor-claude/issues).
MIT, same as disensor.
