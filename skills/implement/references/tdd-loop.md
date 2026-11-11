# TDD loop — the per-task cycle (step 8)

Every task runs `SELECT → RED → GREEN → REFACTOR → GATE → COMMIT`. This is the same cycle whether the runner is the sequential agent, a team `implementer`, or a Workflow stage. The RED step is the load-bearing one — skip its discipline and the whole method collapses into "write code, write a test that happens to pass".

Every transition of that cycle is also written to disk as it happens — see **Status protocol** at the end of this file.

## SELECT

Pick the next task whose `deps` are all `done` — `done` as recorded on disk (`tasks.json` `status`, per the Status protocol), never as remembered from the conversation. In sequential mode that's the topo order; in parallel modes the orchestrator hands it out. **Read the task file first** — `tasks.json`'s `file` field, `docs/features/<slug>/tasks/<task-slug>.md`: it carries the §5 acceptance criteria verbatim, the data delta, the API slice and the edge cases, each signed with its source. `spec.md §5` and the relevant `test-plan.md` rows are the **fallback**, opened when a slice is insufficient, ambiguous, or contradicted by the code ([`./inputs.md`](./inputs.md)); a task with no `file` falls back to them outright. Know, before writing anything, what observable outcome the test will assert.

## RED — write the failing test first

1. Write the test(s) for this task's `acs` **before any production code**. Put them where the repo keeps tests for that layer (detected, not assumed).
2. Run the unit command. Capture the output.
3. **Classify the first run** — this is mandatory and must be stated aloud:

   | Class | What it looks like | Action |
   |---|---|---|
   | **GOOD red** | test compiles, runs, fails on an assertion or «not implemented» | proceed to GREEN |
   | **BAD red** | the test itself won't compile / import-errors / references a symbol that the test got wrong | the test is broken, not the code — **fix the test**, re-run, re-classify |
   | **false-pass** | green on the very first run, before any production code | the test is too weak (asserts nothing real) — **strengthen it** until it's GOOD red |
   | **NON-red** | skipped because its dependency is unavailable (e.g. Docker absent for an integration test) | not a pass and not a fail — record NON-red, governed by `require_integration` |

4. **Quote the failing line** (the assertion + expected-vs-actual, or the «undefined: X» line) before writing any production code. This is the proof that the test exercises the right thing.

### Characterization tasks — the one inverted case

A task whose `acs` are all area-qualified (`orders:AC-02`, from an `extends` baseline — see [`../../tasks/SKILL.md`](../../tasks/SKILL.md) step 4) pins **existing** behaviour, so the expected first run is **green**, not red. Classify it as **GOOD pin** (green, and the assertion encodes the baseline AC's outcome — prove it by temporarily breaking the anchored code line or the expected value and watching it fail, then restore) or **baseline mismatch** (red: the code does not do what the baseline says). A mismatch means the baseline is wrong or the code drifted since it was captured — **stop the task and ask** (fix the baseline AC via `/foresdd:fix <area>`, or correct the test's reading); never edit production code inside a characterization task. On GOOD pin there is no GREEN step; REFACTOR → GATE → COMMIT as usual, and the baseline's §9 «Pinned by» cell is filled with the new test.

A task with only a NON-red integration test and no unit coverage cannot be driven by TDD locally — write the unit-level RED too, and let the integration RED land in CI (the proving-run pattern).

## GREEN — minimal code to pass

Write the **least** code that turns the quoted failing assertion green. No speculative generality, no unrelated edits, nothing outside the task's `files_hint`. Re-run the unit command; confirm the previously-quoted failure is now green and nothing else broke.

## REFACTOR — clean while staying green

Tidy names, extract helpers, remove duplication — re-running the unit command after each change. If a refactor goes red and isn't trivially fixable, **revert it**; the task's job is the GREEN, not the cleanup.

## GATE — the task isn't done until this is clean

Run, per the detected commands + settings:

- **unit** — must be green.
- **integration** — green if available; NON-red recorded if Docker is absent under `require_integration: auto`; BLOCK was already enforced for `always`.
- **lint** (if `gate_lint` and a linter resolved) — clean.
- **vet/typecheck** (if `gate_vet` and a command resolved) — clean.

Any hard-gate failure (unit red, or integration red when it ran, or lint/vet errors) → the task is not done. Fix, or escalate (see [`escalation.md`](./escalation.md)).

## COMMIT — task-scoped, traceable

When `auto_commit: per_task`, commit only this task's files with a message like:

```
<type>(<slug>): <task title>

<one-line what + why>

SDD-Task: T3
SDD-AC: AC-02
SDD-AC: AC-04
```

One `SDD-AC` trailer per AC the task satisfied; the `SDD-Task` trailer ties the commit to `tasks.json`. The task's status files (its `tasks/<task>.md`, `tasks/tracker.md`, `tasks.json`) are set to `done` **before** the commit and ride **in** it, so the commit that lands the code also records it done. (`per_phase` batches a phase's tasks into one commit; `off` leaves committing to the user but still updates every status file.)

**Compile-coupled lane exception.** Tasks in one compile-coupled lane (a shared-contract change + its implementer(s), marked by `tasks` via the shared contract file in `files_hint`) cannot each be committed green alone — the contract change breaks every implementer at compile time. They run **one shared GATE and one commit**: the commit carries an `SDD-Task` trailer **per task** and all of their `SDD-AC` trailers together, and the body names the coupling (e.g. «compile-coupled: T3 interface change + T4 implementation»). This is a sanctioned exception to task-scoped commits, not a license to batch unrelated tasks.

In parallel modes the **lead serializes commits in dependency order** even though the work happened concurrently — the history stays linear and bisectable.

## Status protocol — live task status on disk

`implement` keeps every task's progress on disk, updated **at each transition, not at the end**. A
crashed or interrupted run leaves a tracker that says exactly where it stopped, and the next run
resumes from it.

**Model.** `status` ∈ `todo · in_progress · blocked · review · done`; `step` ∈
`SELECT · RED · GREEN · REFACTOR · GATE · REVIEW · COMMIT` (for `blocked`, the reason). Three status
files carry it, all written together:

| File | Carries |
|---|---|
| `tasks/<task>.md` frontmatter | `status:` + `step:` |
| `tasks/tracker.md` | the task's row — **Status** + **Step** columns |
| `tasks.json` | `status` (optional key; absent = `todo`) — `step` is markdown-only |

**Transitions** (write all three files immediately at each):

| Event | status / step |
|---|---|
| task picked in SELECT | `in_progress` / `SELECT` |
| `test-author` dispatched (or RED begins inline) | `in_progress` / `RED` |
| RED handover accepted (GOOD red quoted) | `in_progress` / `GREEN` |
| `implementer` reports green | `in_progress` / `REFACTOR`, then `GATE` when the gate starts |
| per-task `reviewer` dispatched (team mode, or when configured) | `review` / `REVIEW` |
| commit about to run | `done` / `COMMIT` — set **before** the commit so it rides in it |
| the commit fails (pre-commit hook, conflict) | `blocked` / `COMMIT — <first line of the failure>` — **never** leave `done` on disk without the commit; resume then asks instead of skipping uncommitted work |
| escalation exhausted, or `stop_on_red` halts | `blocked` / `<step> — <reason>` (e.g. `GATE — lint red after 3 retries`) |
| dependents of a blocked task (`stop_on_red: false`) | `blocked` / `dep T<n> blocked` |

`tdd: false` skips the `RED` / `GREEN` handover rows; the rest stand.

**Resume.** At the start of every run (after the DAG is built), read `status` from `tasks.json`:
`done` → skip the task; `in_progress` / `review` → reset to `todo` (that work was never committed —
the code it touched is either uncommitted in the tree or gone; say which tasks you reset);
`blocked` → **ask** the user per task: retry it, or leave it blocked (and its dependents with it).
Missing `status` → `todo`.

**Transit rows are expected.** In team / workflow mode a task's commit carries `tracker.md` / `tasks.json` as they stand at that moment — other tasks may show `in_progress` there. That is harmless: resume resets any non-`done`, non-`blocked` row to `todo`.

**Who writes — one writer per run, never two.**

- **Sequential** — the engine writes the three files after every subagent returns. The status files
  ride in the task's own commit.
- **Team** — the **lead** writes them after every teammate handover; teammates never touch the status
  files. The lead also makes the task's commit: it applies the teammate's worktree diff in the main
  checkout, adds the status files, and commits once ([`team-exec.md`](./team-exec.md) §Commits).
- **Workflow** — the script has no file-system access, so stage agents **do not** write status. After
  each Kahn layer the generated script runs **one `close-layer` agent** in the main checkout that
  receives the layer's collected verdicts, writes status + step for every task of the layer, rebuilds
  `tracker.md` / `tasks.json`, and commits the layer's tasks serially in dependency order
  ([`workflow-exec.md`](./workflow-exec.md)). Status in this mode moves per layer, not per stage.

**The native task list is a mirror, never the source.** When the session exposes `TaskCreate` /
`TaskUpdate`, the orchestrator (sequential engine, team lead, or the main session around a Workflow)
creates one native task per `T<n>` once the user says **Start** (step 7) and updates it at each transition — status
(`pending` / `in_progress` / `completed`) plus an `activeForm` naming the step («T3 · GREEN —
implementing order validation»). In team mode teammates may claim/complete native tasks themselves;
the lead only fills the gaps. No such tools (newer models without `CLAUDE_CODE_ENABLE_TODO_TOOLS`)
→ skip silently ([`../../allocations/fallbacks.md`](../../allocations/fallbacks.md)).
On any disagreement the three status files win.

## Progress output — what the user sees while it runs

The status files are for the next run; the progress line is for the person watching this one.
**Every time the status files are written, the same writer prints one line** — no test output, no
diff, just where the run is:

```
── wave 2/4 · T3, T4 (parallel) ──────────────────────────────
[2/8] T3 preferences repository · RED ▶
[2/8] T3 · RED ✓ GOOD red — `expected 1 row, got 0` (preferences_repo_test:42)
[2/8] T3 · GREEN ✓
[2/8] T3 · GATE ✓ unit ✓ · integration ✓ · lint ✓ · vet ✓
[3/8] T3 · COMMIT ✓ a1b2c3d
[3/8] T4 · GREEN ✗ retry 1/3 — `undefined: prefs.Validate`
[3/8] T4 · ⛔ blocked — GATE — lint red after 3 retries · dependents blocked: T6
```

- **Counter** `[done/total]` — tasks committed so far / all tasks in `tasks.json` (resumed `done` tasks count).
- **Glyphs** — `▶` step started · `✓` step passed · `✗` attempt failed (with `retry n/max_red_retries`) · `⛔` blocked · `NON` integration skipped (Docker absent).
- **Detail** — only on RED (the quoted failing line: the proof the test is right), on a failure (its
  first line), on COMMIT (the short SHA), and on blocked (the reason + the dependents it takes down).
- **Wave header** — printed when a new Kahn layer starts, naming its tasks and whether they run in parallel.

**Who prints** — the same single writer as the status files. Sequential: the engine, after each
subagent returns. Team: the lead, after each handover. Workflow: stage agents can't print to the
user, so the main session prints the wave header when the script starts a layer and one line per
task from each `CLOSE_VERDICT` (status moves per layer in this mode — say so once in the first
header: «progress updates per wave»).

### Run summary (step 10)

At the end, before the handoff block, one table — every task, final state:

```
| Task | Title                       | Status  | Commit  | unit · int · lint · vet | ACs          |
|------|-----------------------------|---------|---------|-------------------------|--------------|
| T1   | add preferences table       | done    | 9f1e2aa | ✓ · ✓ · ✓ · ✓           | AC-01        |
| T3   | preferences repository      | done    | a1b2c3d | ✓ · NON · ✓ · ✓         | AC-02        |
| T4   | update-preferences use case | blocked | —       | ✓ · — · ✗ · —           | AC-03, AC-05 |
| T6   | PUT /preferences handler    | blocked | —       | dep T4 blocked          | AC-04        |

ACs covered: 3/5 — AC-03, AC-05 open (T4 blocked) · AC-04 open (T6 blocked)
Commits: 4 · NON-red integration: T3 (docker unreachable, require_integration=auto)
```

`✓` green · `✗` red · `NON` skipped by policy · `—` not run / not configured. An AC counts as
covered only when **every** task listing it is `done`.
