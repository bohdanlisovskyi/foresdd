# Write as you go, commit per document — the disk + git contract every artifact skill follows

> **Reference-only.** Not a skill. Every skill that writes a pipeline document follows this file
> for **when** the document lands on disk and **how** it is committed. Skills keep a one-line
> pointer («Commit per [`write-and-commit.md`](../allocations/write-and-commit.md)») plus their own
> list of documents; the rules live only here.

## 1. Progressive writes

- **Bootstrap at the first write point.** The first time the skill has something real to write,
  it copies the artifact's template to its target path (frontmatter stamped, every section still a
  placeholder). From then on the file on disk is the artifact — not a draft in the conversation.
- **Write each resolved unit immediately.** A section, an AC, a row, a step, a screen, a finding —
  whatever the skill's unit is — goes to disk right after its resolution: `Approve`, `Edit` (after
  the final answer), `Save as Open Question` (the OQ row too), or, for a skill with no dialogue,
  right after it is generated. `Drop` writes the removal. Never hold the document in memory and
  write it once at the end.
- **Re-read before you patch.** Patch the file as it is on disk *now*, not as you last wrote it —
  the user may have edited it in their editor mid-step. Keep their edits; if one contradicts a
  resolved unit, ask instead of overwriting.
- **Resume, don't clobber.** If the target file already exists with uncommitted changes when the
  step starts (an earlier session crashed or was `/clear`ed), show what's there and ask once:
  **Resume** (continue from the disk; treat filled sections as already resolved) or **Restart**
  (re-bootstrap from the template). Never overwrite it silently.
- **Downstream readers read the disk.** The clean-context critic (read-only) and the structural
  self-check ([`self-check.md`](./self-check.md)) read the file from disk; the skill patches the
  file with whatever the user accepts from the critic's findings.
- **Exceptions** (no progressive write, by design):
  - `interview` in its no-write mode (Plan Mode, headless, outside a git repo) — it writes nothing
    at all; its own SKILL.md rules win.
  - single-line writers (`tshirt-size`'s `.size` + `.route`; the feature's `.depth` per
    [`interview-depth.md`](./interview-depth.md)) — written once, which already *is* immediately.

## 2. Commit at the end of the step — one commit per document

**Code stages differ.** `implement` and `fix` commit **per task / per fix** after that unit's GATE
(with `SDD-Task` / `SDD-Fix` trailers) — their own SKILL.md rules govern; the guards in §3 and the
`git commit -- <paths>` discipline still apply. Everything below is about **document** stages.

**Order is fixed:** structural self-check passes → commit plan → commits → stage-handoff block. A
failed or unresolved self-check means **zero commits** — say so in the handoff and leave the files
uncommitted for the user to inspect. The one exception is an explicit **Commit anyway** from the
user ([`self-check.md`](./self-check.md) «When an item stays unresolved»): commit as planned with the
body line `self-check override: <item label>`. Never infer the override — headless runs leave the
files uncommitted. Progressive writes protect against a lost session; commits
mark a finished, checked document.

### 2.1 The commit plan — one document, one commit

Before the first commit, write the plan down: one line per commit, with its exact paths. **The
default is one document per commit.** Only these sets may share a commit — nothing else, ever:

| Set (one commit) | Why together |
|---|---|
| a migration pair `*.up.sql` + `*.down.sql` | one change; a lone half is broken |
| `.size` + `.route` | one classification |
| the whole `tasks/` directory + `tasks.json` | one model rendered twice (`tasks` contract) |
| a skeleton materialized by `scaffold` | one bootable unit |
| the `.gitignore` patch from [`settings-file.md`](./settings-file.md) | rides in the step's **first** commit; the settings file itself is never committed |
| a newly written or changed `.depth` ([`interview-depth.md`](./interview-depth.md)) | a one-line setting, not a document — rides in the step's **first** commit |

Pairs that are **always separate** commits (the usual bundling mistakes):

- `spec.md` ≠ `.size` + `.route` ≠ `CONTEXT.md` ≠ `roadmap.md`
- `sad.md` ≠ each ADR — every ADR is its own commit, separate from the document that cites it
  (`sad.md`, `docs/architecture-map.md`)
- `data-model.md` ≠ each migration pair
- two ADRs, or two migration pairs, never share a commit

If a document isn't in the table, it gets its own commit. When unsure, split.

### 2.2 Commands (per planned commit)

```bash
git status --porcelain -- <paths>          # empty → nothing changed, skip this commit
git add -- <paths>
git commit -m "<stage>: <slug> <doc>" \
  --trailer "SDD-Stage: <stage>" \
  --trailer "SDD-Feature: <slug>" \
  -- <paths>
git show --name-only --format= HEAD        # must list exactly <paths>
```

- **Verify every commit.** If `git show --name-only` lists anything beyond the planned paths (or
  misses one), stop: report the mismatch and don't make further commits. Never `--amend` to fix it.
- An empty `git status` is normal (`clarify` that resolved nothing in-file, `review` with no spec
  defer, an unchanged `.pen`) — skip silently; never create an empty commit.
- `git commit -- <paths>` commits exactly those paths, so whatever the user has staged elsewhere
  stays staged and out of the commit.
- **Never** `git add -A` / `git add .` / `git commit -a`, `--no-verify`, `--amend`, force anything.
- **Subject:** English, `<stage>: <slug> <doc>` — e.g. `specify: checkout-v2 spec.md`,
  `data-model: checkout-v2 migration 0003_orders`, `design: checkout-v2 ADR-0004 event bus`.
  Repo-level documents drop the slug (`survey: architecture-map.md`).
- **Trailers:** `SDD-Stage: <stage>` always; `SDD-Feature: <slug>` for feature documents (omit it
  for repo-level ones). They make `git log --grep "SDD-Feature: checkout-v2"` list a feature's
  whole document history. Any attribution trailer the host requires goes after them. Git older
  than 2.32 has no `--trailer`: put the trailers in a second `-m` paragraph instead.
- **Branch:** document stages commit to the **current** branch, the default branch included.
  `branch_strategy` is an `implement` rule only. A detached HEAD is a guard (§3).

## 3. Guards — when not to commit

Check these once, before the first commit of the step.

| Situation | Do |
|---|---|
| not a git repo | write files, no commits; say so in *What I did* |
| detached HEAD (`git symbolic-ref -q HEAD` fails) | write files, no commits; print the §2.2 commands in the handoff |
| merge / rebase / cherry-pick in progress (`.git/MERGE_HEAD`, `rebase-merge/`, `rebase-apply/`, `CHERRY_PICK_HEAD`) | don't commit; say so; the user finishes their operation first |
| `auto_commit: off` in `.claude/sdd.local.md` | don't commit; print the ready-to-run §2.2 commands in the handoff |
| the user has the same file **partially** staged (`git diff --cached` and `git diff` both touch it) | warn before committing: the commit takes the whole on-disk version of that file |

Failures **during** a commit:

| Failure | Do |
|---|---|
| pre-commit hook fails and **modified only the planned paths** (formatter, `--fix` linter) | `git add -- <paths>`, retry that commit **once**; a second failure → the next row |
| pre-commit hook fails otherwise (no edits, edits outside `<paths>`, or a failed retry) | show its output, stop committing, print the remaining commands; never `--no-verify` |
| any other `git commit` error (no `user.name`/`user.email`, GPG signing, `index.lock` exists) | show the error, stop, print the remaining commands; never edit git config, disable signing, or delete the lock |

`auto_commit` is shared by every stage: `per_task` and `per_phase` both mean «commit» for a
document stage (the task/phase distinction only shapes `implement`); `off` means «print the
commands, don't run them».

## 4. Report

*What I did* in the stage-handoff block ([`handover.md`](./handover.md)) lists every commit made,
short SHA + subject, one per line:

```
- committed `a1b2c3d` specify: checkout-v2 spec.md
- committed `d4e5f6a` specify: checkout-v2 .size+.route
```

Every planned commit that didn't happen is named with its reason (nothing changed, guard hit,
hook failure, `auto_commit: off`), followed by the commands to run it.

## Anti-patterns

- **Bundling documents.** `spec.md` + `.size`, or `sad.md` + an ADR, in one commit — they revert
  independently. Only the §2.1 sets share a commit.
- **The whole document written at the end.** A crash or a `/clear` loses every decision so far.
- **Per-section or bootstrap commits.** Twelve commits for one SAD bury history; the disk already
  holds the partial work.
- **Committing before the self-check.** A commit should mark a checked document.
- **`git add -A` / `git commit -a`.** Sweeps in the user's unrelated work.
- **"Fixing" a bad commit with `--amend` or `--no-verify`.** Stop and report instead.
