---
name: config
model: inherit
effort: medium
agents: []
description: >
  Use to create and tune the per-project settings file `.claude/sdd.local.md` — the one place that
  decides how deeply the pipeline interviews you, which model tier its judgment agents run at, how
  strict the TDD gates are, and how tasks execute and commit. Triggers on "config", "settings",
  "configure sdd", "tune the pipeline", "change the judgment model", "set the interview depth",
  "/foresdd:config", "/foresdd:config depth" (any one group by name, or a direct «set interview depth
  to hard»). Creates the file with documented defaults FIRST (so you have a working config before
  answering anything), shows the current settings as a short table (group → current → default or
  custom), then either applies a targeted change to just the group you named, or asks the four
  grouped questions (or just one group you pick), and patches only the keys you confirm —
  preserving your comments, key order and unknown keys. Never touches the pipeline's artifacts; the settings file is gitignored, only the
  .gitignore patch is committed.
---

# Skill: config

The settings file has many creators and **one editor: this one**. Six pipeline skills
(`interview` / `survey` / `roadmap` / `scaffold` / `specify` / `implement`) — and this skill too —
write `.claude/sdd.local.md` with documented defaults, so the pipeline always finds a real file.
None of the six offers to change a value. That offer lives here, and only here.

Everything about the file itself — the template, the create procedure, the `.gitignore` patch, the
key semantics, the edit rules — is canonical in
[`../allocations/settings-file.md`](../allocations/settings-file.md). This skill is the **conversation**
over it.

## Owner

Whoever owns the repo's setup — usually the lead who runs the pipeline first, once per project.

## Inputs

- Nothing is required. No gate, no upstream artifact: a bare repo is a valid starting point.
- (Optional) an existing `.claude/sdd.local.md` — read, diffed against the defaults, patched in
  place. Never regenerated.

## Protocol

1. **Ensure the settings file (first thing — this skill has no input gate).** If `.claude/sdd.local.md`
   is absent, create it now from the canonical template — documented defaults + the self-documenting body — and
   patch `.gitignore`; if it exists, read it and never overwrite. The one procedure lives in
   [`../allocations/settings-file.md`](../allocations/settings-file.md). Creating is unconditional;
   **changing values is offered here and nowhere else**. Say the one-line creation notice from the
   canon (only when the file was just created). Here that line is the opening move, not a footnote:
   the user has a working config before the first question.

2. **Read the current state and show it as one table.** One row per decision group plus two
   housekeeping rows, in this order: Interview depth · Model tier · Tests and gates · Execution and
   commits · Commands · Other keys. Columns: **Group** · **Current** · **Status**.
   - *Current* is the **option label** the group matches in [`./references/interview.md`](./references/interview.md)
     (e.g. «Full gates, stop on red»), followed by the key(s) that make it so in backticks only when
     they differ from the defaults. A group that matches no option reads `custom:` plus the odd
     key(s) out, e.g. `custom: gate_lint false`.
   - *Status* is `default` or `custom`. *Commands* reads «autodetect» or the pinned `cmd_*` keys.
     *Other keys* lists unknown keys by name (preserved verbatim — say so) or «none».
   Below the table, one line for anything that needs attention, and nothing when all is well.
   Name any key with an **invalid value** (it is running on its default per the canon's
   reading semantics). **A malformed frontmatter is never repaired silently** — print the lines
   that failed to parse and offer exactly two ways forward: rewrite from the template (naming what
   will be lost) or stop so the user fixes it by hand. If `settings_version` is absent or older
   than the template, run the **upgrade offer** per the canon's «Upgrading an older file» — one
   question, before the fork — and patch what the user picks.

3. **Targeted request? Skip the fork.** If the invocation names a group or a key, go straight to
   that group. This covers an argument (`/foresdd:config depth`), a key=value
   (`interview_depth=hard`) or plain words («set interview depth to hard», «turn off the lint
   gate», «put the judges on sonnet»). Resolve the name through the **group aliases** in
   [`./references/interview.md`](./references/interview.md).
   - **Value given and valid** (`interview_depth=hard`, «turn off lint») → write exactly that key,
     no question. The user already decided. Go to step 5.
   - **Group named, no value** («change the model tier») → ask only that group's question (step 4),
     then step 5.
   - **Ambiguous name or invalid value** → say which part didn't resolve (for a value, name the
     valid set) and ask that group's question. If even the group is unclear, fall through to the fork.

   **Otherwise, one forking question** per [`../allocations/style.md`](../allocations/style.md):
   «Keep defaults» / «Walk the four questions» / «Change one group». «Keep defaults» (or «Keep
   as is» on a repeat run) → skip to step 6 and print the handoff; the file is already on disk
   and working, so this is a legitimate exit, not an abort. «Change one group» → one follow-up
   question with the four groups as options (each showing its current value from the step-2
   table), then only that group's question.

4. **Ask the grouped questions — all four in three `AskUserQuestion` calls, or only the targeted group.** Questions are grouped by
   **decision**, not by key — a person tunes «how strict are the gates», not `gate_vet`. The four:
   model tier · strictness and gates · execution and commits · interview depth.
   Together they cover **20 of the 24 setting keys** (`settings_version` is meta and never asked). The four `cmd_*` keys are **not
   asked**: empty means the detection cascade reads the repo's own Makefile / package scripts /
   manifests, which is the better answer than a pinned command that rots. Verbatim wording, the
   options, and the question → keys map → [`./references/interview.md`](./references/interview.md).
   Model tier is asked **directly** rather than probed, because the session cannot enumerate the
   models an account actually has.

5. **Write the confirmed keys, key by key.** Patch only the lines whose values were confirmed;
   preserve comments, key order and unknown keys exactly. A commented-out key is pinned by
   uncommenting its line, and returned to its adaptive default by commenting it back out — never
   by adding a second copy. Print a `old → new` line per changed key (`(default)` for a
   commented-out side),
   and **separately** list what was **derived rather than asked** — the model / `effort_*` keys left
   on their adaptive defaults, and the `cmd_*` keys left empty for autodetect. A value the user did
   not choose must never read as if they had. On a targeted run, the groups that weren't touched get
   one line («unchanged: model tier, execution and commits, interview depth») instead of a derived
   list. A key written straight from a key=value or plain-words request is marked `(set directly)`.
   When the change takes effect matters, say it: for example, `interview_depth` applies only to
   features that don't yet have a `.depth`. Nothing else on disk is touched.

6. **Structural self-check + handoff.** Run the **structural self-check** per
   [`../allocations/self-check.md`](../allocations/self-check.md) — re-read the file **from disk** and verify
   **6 items**: (1) `.claude/sdd.local.md` exists (`test -f`); (2) its frontmatter parses and every
   confirmed key holds the confirmed value; (3) every key present before the run is still present —
   none dropped, including unknown ones (a key commented out on the user's instruction still counts
   as present), and no key appears twice; (4) every inline comment and group header that was there is still there;
   (5) `.gitignore` contains `.claude/*.local.md` and `.worktrees/`, each exactly once; (6) no file
   outside `.claude/sdd.local.md` + `.gitignore` was modified (`git status --short`). Fix + re-check
   ≤2 cycles; surface anything unresolved. Then commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md):
   one commit `config: .gitignore sdd settings` **only if `.gitignore` actually changed** — the
   settings file is gitignored and has nothing to commit. Then **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md)
   — *What I did* (the changed keys + the self-check line + the commit SHA or «nothing to commit») + *Review* (`.claude/sdd.local.md`) +
   *Run next* (utility variant: `/clear` optional, resume your backbone stage — name the likely one).

## Definition of Done

- `.claude/sdd.local.md` exists and parses, whichever branch the run took (defaults or tuned).
- The current settings were shown as the step-2 table before anything was asked.
- Every key the user confirmed (or set directly) holds that value; every key they didn't confirm is
  byte-identical to what was there before.
- Unknown keys, key order and inline comments survived the run.
- Every derived value (unchanged `effort_*`, autodetect) was named out loud, separately from the asked ones.
- `.gitignore` covers `.claude/*.local.md` and `.worktrees/`.
- The 6-item check in step 6 is this skill's structural self-check; its result is one line in the
  handoff.

## Anti-patterns

- **Asking before creating.** The file lands with documented defaults first; a user who answers
  nothing still ends up better off than before the run.
- **Regenerating the file from the template** because a key looked stale. That is how a
  hand-written comment or a hand-added key disappears. Patch key by key.
- **Walking all four groups for a one-key change.** «Set depth to hard» is a decision already
  made. Write it, show `old → new`, done.
- **Re-bundling a targeted edit.** Writing `gate_lint: false` alone leaves the group as
  `custom: gate_lint false`. Don't "complete" it into the «Light gates» preset.
- **Asking about `cmd_*`.** Empty = autodetect, which is the recommended answer; asking invites a
  pinned command that goes stale.
- **A settings question inside another skill.** The six pipeline skills create and read.
  Only `config` tunes.
- **Touching pipeline artifacts.** This skill writes two files and no others.

## References

- [`../allocations/settings-file.md`](../allocations/settings-file.md) — the canonical template, procedure and key semantics.
- [`./references/interview.md`](./references/interview.md) — the four questions verbatim, the question → keys map, and the group aliases for targeted runs.
- [`../allocations/style.md`](../allocations/style.md) — how every question is phrased.
- [`../allocations/fallbacks.md`](../allocations/fallbacks.md) — what each stage does when a mechanism (`TeamCreate`, `Workflow`, a model tier) is unavailable.
- [`../allocations/agent-roster.md`](../allocations/agent-roster.md) — what the model tier actually changes.
- [`../implement/references/settings.md`](../implement/references/settings.md) — the engine-side delta.
