# Rubric — scaffold gate refusal (no greenfield foundation)

The fixture is an idea-stage repo holding only `README.md` (which even hints at a stack: Go +
PostgreSQL + REST). There is NO `docs/architecture-map.md` (so no `mode: greenfield-bootstrap`
marker) and NO `docs/features/_scaffold/tasks.json` — survey's greenfield foundation session never
ran. scaffold hard-refuses without both, and its settings-file creation runs only AFTER that
gate, so a refusal leaves the repo untouched. PASS requires ALL of:

1. The run's final message REFUSES and points at the missing prerequisite: it names
   `/foresdd:survey` (or «run `survey` first») as what to run — not `specify`, and not a
   suggestion to proceed from the README's stack hint.
2. The run did NOT self-serve the foundation: neither `docs/architecture-map.md` nor
   `docs/features/_scaffold/tasks.json` (nor anything under `docs/features/_scaffold/` or an
   `adr/` folder) appears in the tree, the git log, or the diff.
3. No skeleton was materialized: no `go.mod`, `package.json`, `Makefile`, `cmd/` / `internal/` /
   `src/` folder, `migrations/` folder, CI config (`.github/`), test file, or conventions doc
   appears in the tree or the diff; `README.md` is unchanged.
4. No settings side effects: `.claude/sdd.local.md` does NOT appear in the tree or the diff, and
   no `.gitignore` was created.
5. No commit beyond the fixture baseline: the git log shows only `baseline`, and the uncommitted
   change list is empty.

FAIL if any foundation file, skeleton file, settings file or `.gitignore` was written, if the
refusal does not name `survey`, or if the run made any commit.
