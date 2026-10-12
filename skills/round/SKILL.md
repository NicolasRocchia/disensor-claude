---
name: round
description: Run the adversarial review round with the disensor CLI and declare its residue, when the user invokes it to close a plan, a diff or an architecture decision, or to fill the declaration a round produced.
disable-model-invocation: true
---

This skill drives the `disensor` CLI, installed and set up with
`/disensor:setup`. It runs only when the user invokes it: the round sends the
material under review to the reviewer the owner registered and consented to,
and that is the owner's call every time.

Four rules that sit above the runbook below:

- Start with `disensor --version`. This plugin was written for 0.12.1; if the
  shell resolves another version, say so and stop.
- If the tree is not clean, say so and let the user commit. Do not commit,
  stash or discard anything for them.
- A candidate reviewer outside the catalogue is an executable that will later
  receive the material under review. Do not run it, not even with `--help`,
  before the owner approves registering it.
- When more than one round ran, the declaration lists the findings of every
  round, not only the last report. A clean last report does not erase what the
  earlier ones found.

# Running a review event

`disensor` does the mechanical half: it decides whether a round is required,
builds the package, runs the reviewer, captures the report and anchors the
result. You do the half that needs judgement: checking findings against the
code, deciding what to incorporate, and telling the story in the pull request.

Never paste material between models by hand. If something cannot be automated,
say so instead of doing it manually and calling it a round.

## 1. Before the round

The tree has to be clean: a diff round reviews commits that already exist.
Commit your work first. The runner will not stash for you.

## 2. Run it

```
disensor round --gate diff --generator-family <your family> \
  --base <target branch> --head HEAD \
  --result <path outside the repository>
```

Read the exit code, do not guess from the text:

- `0`: the round ran. Its report and result are where you asked for them.
- `3`: no review required. The policy of this repository says these paths do
  not demand one. Go to the pull request; the gate will agree.
- `4`: no reviewer answered. Run `disensor reviewer suggest`. The catalogue is
  a shortcut, not the list of what is allowed: ANY assistant with a command
  line can review, whatever the vendor. Look at what this machine actually has,
  read its `--help`, and register it. An entry outside the catalogue needs the
  OWNER to approve it, so ask; do not approve it yourself. If the round says
  the material of this repository was not authorised, stop there too: the
  consent to send it out of this machine is the OWNER's, given with
  `disensor reviewer consent <id>`. Never run that command yourself, not even
  after the owner approved the round in the chat: ask them to run it.
- `5`: the tree changed during the round. Do NOT declare. Tell the user what
  appeared: a reviewer that writes is not a reviewer that only reads.
- `6`: could not decide whether a round was needed. Stop and report. This is
  never a green light.

For a plan or an architecture decision, pass `--gate plan` or `--gate architecture` with `--material <file>`:
that material does not live in the git range, and the scope cannot trigger it.
Deciding that a plan crosses the impact bar is your judgement.

## 3. Read the report and verify

Check EVERY finding against the actual code before accepting it. The reviewer
is decorrelated, not right, and an unverified finding is not a finding. Fix
what is real, refute what is not, with evidence.

## 4. If you changed anything, run the round again

The rule is the freshness of the material, not the verdict of the report. If
you incorporated even a minor finding, HEAD moved and the previous round no
longer covers what is going to be merged. `disensor new --round` will refuse
the stale result, which is the mechanism working, not an error to route around.

## 5. Declare

```
disensor new --gate <the gate of the round> --level <A|B|C> --round <result>
```

It arrives prefilled with what the runner observed: reviewer, anchors, hashes,
the reviewer's wall time as `reviewer_seconds` in the extension space, and the
residue items that a degraded round owes. `metrics.extra_time_sec` is the
whole cycle, not the reviewer: fill it only if you timed it. Fill in the findings with
their terminal states and the residue with what stayed open. The filling guide in `references/guide.md`, next to this file, explains every field. Do not invent findings or states: the artifact declares
what happened, not what should have happened.

Then `disensor validate` until it says VALID, and commit the declaration in its own commit, never mixed with code. Then `disensor gate --no-comment --base <target branch> --head HEAD` has to be green: the gate reads the declarations that are committed in that range.

## 6. The pull request

Its body tells the whole event: what changed, which reviewer attacked it, every
finding and what was done with it, and what stayed open. That is what the human
arbiter reads.

## When to stop and ask

- A risk that somebody has to accept (`owner_decision`).
- A finding escalated without resolution (`escalated_open`).
- No reviewer available, or an entry that needs approval.
- The consent to send the material to a reviewer is missing: the owner gives
  it, never you.
- The tree changed during a round.

<!-- disensor:block v0.11 -->
