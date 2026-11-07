---
name: scaffold
model: inherit
effort: medium
agents: []
description: >
  Use to materialize the greenfield skeleton that survey's foundation session planned. Reads
  docs/architecture-map.md (mode: greenfield-bootstrap) plus docs/features/_scaffold/tasks.json
  and builds the real project structure: folders + entry point, test harness + smoke test,
  migration tooling, CI, the conventions doc. Triggers on "scaffold the skeleton", "materialize
  the skeleton", "bootstrap the project skeleton", "/foresdd:scaffold". Runs the S-tasks sequentially
  inline (no team/workflow orchestration), anchored on the skeleton smoke test — builds + boots +
  empty test suite runs + migration tool runs — commits, and hands off to /foresdd:specify.
  Hard-refuses without the greenfield foundation: run survey first.
---

# Skill: scaffold

The **materialization step between `survey`'s greenfield foundation and the first feature.** `survey`
fixes the foundation (stack / structure / conventions in `docs/architecture-map.md`, marked
`mode: greenfield-bootstrap`) and emits the scaffold plan (`docs/features/_scaffold/tasks.json`,
tasks S1–S5 per [`../survey/references/foundation.md`](../survey/references/foundation.md));
`scaffold` turns that plan into a repo that **builds, boots, tests and migrates** — then the normal
per-feature flow (`specify → … → implement`) builds into it. This skill exists so the greenfield
handoff is a real gate, not a wave of the hand: `_scaffold` is **not a feature** (no `.size`, no
`.route`, no ACs), so it never enters `implement`'s engine or its team/workflow decision tree.

**The skeleton smoke test is the TDD anchor** (canonical here). Scaffold tasks have no feature ACs,
so red→green anchors on the structural smoke test: **RED** = the project does not build / boot / the
tooling doesn't run; **GREEN** = build + boot + the empty test suite + the migration tool all
succeed. That keeps the discipline meaningful for structural work — no per-folder TDD theatre.

## Owner

Architect / Tech Lead — the same person who fixed the foundation in `survey`.

## Inputs

- `docs/architecture-map.md` with `mode: greenfield-bootstrap` — the decided stack, module
  structure, conventions, and the machine keys (`build_cmd`, `test_cmd`, `lint_cmd`,
  `migration_tool`, `frontend`).
- `docs/features/_scaffold/tasks.json` — the S1–S5 scaffold plan (`layer: scaffold`, `slug: "_scaffold"`).

## Protocol

1. **Hard gate.** Both inputs must exist: `docs/architecture-map.md` whose frontmatter says
   `mode: greenfield-bootstrap`, AND `docs/features/_scaffold/tasks.json` parsing as the scaffold
   contract (`slug: "_scaffold"`, `layer: scaffold` tasks with `id`/`title`/`deps`/`dod`/`files_hint`).
   Either missing → **refuse** with the blocked handoff, *Run next* `/foresdd:survey` on its own line:
   «its greenfield session fixes the foundation and emits the scaffold plan — then come back here».
   A map without the greenfield marker means the repo is already real — refuse too and point at
   `/foresdd:specify <slug>`. If the skeleton already exists (every S-task's output present and the
   smoke test green), say so and STOP — nothing to materialize. **Partly there** (some S-tasks'
   `files_hint` outputs exist — an interrupted earlier run) → resume: say which tasks look done,
   re-verify their `dod`, and continue from the first incomplete one; never regenerate files that
   already pass.
2. **Ensure the settings file (first thing, after this skill's own gate).** If `.claude/sdd.local.md` is
   absent, create it now from the canonical template — documented defaults + the self-documenting
   body — and patch `.gitignore`; if it exists, read it and never overwrite. The one procedure
   lives in [`../allocations/settings-file.md`](../allocations/settings-file.md). Creating is
   unconditional; **changing values is only ever offered by [`config`](../config/SKILL.md)**. Say the
   one-line creation notice from the canon (only when the file was just created).
   **Then read the foundation.** From the map: stack, folder/module structure, conventions catalog, the
   machine keys. From `tasks.json`: the S-tasks in dependency order. The map is the **only** source
   of decisions — scaffold never re-litigates stack/style choices (that was `survey`'s session).
   **Then preflight the toolchain — before writing a single file.** Check that every executable the
   machine-key commands need is on `PATH` (`command -v <tool>` for the language toolchain, the
   package manager, the migration tool, the linter) and, when the map names a datastore, that one
   is reachable for the migration apply + revert (a running local server, or a container runtime
   to start one). Report the result as a short checklist. **Toolchain missing** → stop with the
   blocked handoff: list each missing tool with the one install hint for this platform, write
   nothing — a half-written skeleton that can't build is worse than none. **Only the datastore
   missing** → one `AskUserQuestion`: **Start it and I'll retry** / **Scaffold now, verify
   migrations later** (the migration task still writes its files; its apply + revert is recorded
   under *Needs your attention* as unverified, and the run ends `⚠️`, never `✅`) / **Stop**.
   **Then preview the plan** in one short list — each S-task by title with the top-level paths it
   will create — so the user knows what's about to land; no confirmation question (the decisions
   were confirmed in `survey`).
3. **Materialize sequentially inline.** Execute the S-tasks one by one in dependency order, in this
   session — deliberately **no** agent team, no Workflow, no `implement` decision tree: `_scaffold`
   has no `.size`/`.route`, and five structural tasks need no orchestration. Per task: create the
   files its `files_hint` names, to the map's conventions; verify its `dod`; record it done. A task
   that genuinely doesn't apply (e.g. no datastore → the migration task) is **explicitly dropped
   with a stated reason** — never silently skipped.
4. **Drive the smoke test green.** Write the smoke test as part of the harness task, then run the
   full anchor with the map's machine-key commands: build + boot + the empty test suite + the
   migration tool (apply + revert). Iterate until GREEN — a red skeleton is not done — but
   **bounded**: at most 3 fix attempts per failing check. Still red after that → stop without
   committing and emit the `⚠️` handoff with the failing command, the last ~20 lines of its
   output, what was tried, and the likeliest cause (a toolchain version mismatch, a port in use, a
   foundation gap that belongs back in `survey`). Say one progress line per check as it goes
   («build ✓ · boot ✓ · tests … »), so a long run never looks hung.
5. **Reconcile the map's machine keys.** If the commands that actually worked differ from the map's
   frontmatter (`build_cmd` / `test_cmd` / `lint_cmd` / `migration_tool`), **update the map** —
   `implement`'s command-detection cascade reads these keys; stale keys poison every later feature.
6. **Structural self-check** — per [`../allocations/self-check.md`](../allocations/self-check.md), **before
   any commit**: verify **4 items**: (1) the smoke test was actually executed and is green (build +
   boot + empty suite + migration tool — command output in hand, not assumed; the migration
   apply + revert may instead be *owner-deferred* from the preflight, and then it is listed as
   unverified, never counted as green); (2) every S-task is
   done or explicitly dropped with a reason; (3) the map's machine keys match the commands that just
   ran (updated if they diverged); (4) every file the S-tasks' `files_hint` names exists on disk and
   is not gitignored. Fix + re-check ≤2 cycles; surface anything unresolved — an unresolved item
   means no commits.
7. **Commit** per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — the skeleton
   is one indivisible commit (`scaffold: materialize skeleton`, paths = the materialized files +
   the settings `.gitignore` patch); the map, if step 5 changed it, is a **separate** commit
   (`scaffold: architecture-map.md machine keys`).
8. **Handoff.** Emit the **stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) —
   *What I did* (tasks materialized, smoke-test result, «self-check: 4/4 pass», the commits with short SHAs) + *Review before
   continuing* (the committed skeleton diff + `docs/architecture-map.md`) + *Run next*: `/clear`,
   then `/foresdd:specify <slug>` — the first real feature, with a real repo to build into.

## Definition of Done

- Every S-task from `docs/features/_scaffold/tasks.json` is materialized (or explicitly dropped
  with a reason), to the conventions the map fixes.
- The skeleton smoke test is **green**: the project builds, boots, the empty test suite runs, the
  migration tool applies + reverts (or that one check was owner-deferred at preflight and is
  flagged unverified in the handoff).
- The map's machine keys reflect the commands that actually work; the skeleton is committed.

## Anti-patterns

- **Orchestrating five structural tasks.** No team mode, no Workflow, no DAG engine — `_scaffold`
  is repo-level bootstrap, not a feature; sequential inline is the design, not a fallback.
- **Per-folder TDD theatre.** The smoke test is the one anchor; writing a failing test per directory
  is ceremony without information.
- **Re-deciding the foundation.** Stack/structure/convention choices live in the map + its ADRs
  (`survey`'s session); scaffold materializes, it never re-litigates. A gap in the map goes back to
  `survey`, not into an improvised decision here.
- **Handing off red.** «Skeleton written but doesn't boot» is not done — GREEN is the exit condition.
- **Discovering a missing toolchain by failing the build.** The preflight exists so the user hears
  «install X» before anything is written, not after five tasks of output and a stack trace.
- **Retrying forever.** Three honest attempts, then a clear report — an endless fix loop burns the
  session and hides the one thing the user could fix in a minute.
- **Treating `_scaffold` as a feature.** No `.size`/`.route`, no spec, no ACs — it never enters the
  per-feature pipeline or its size/route machinery.
