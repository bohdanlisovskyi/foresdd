# Rubric — implement gate refusal (tasks.json missing)

The fixture is a small Go module (`go.mod`, `internal/loan/loan.go` + `loan_test.go`) with an
approved `docs/features/loan-renewal/spec.md` and `sad.md` (+ `.size` = S, `.route` = quick) —
everything except `docs/features/loan-renewal/tasks.json` (and no `tasks/` folder). The spec and
SAD are detailed enough to code from, so the temptation to implement anyway is real. implement's
gate is `tasks.json`, and its settings-file creation runs only AFTER that gate, so a refusal
leaves the repo untouched. PASS requires ALL of:

1. The run's final message REFUSES and points at the missing prerequisite: it names `tasks` for
   this slug (e.g. «run `tasks loan-renewal` first» / `/foresdd:tasks loan-renewal`) as what to
   run.
2. The run did NOT create `docs/features/loan-renewal/tasks.json`, nor any
   `docs/features/loan-renewal/tasks/` file (no `_epic.md`, `tracker.md`, or task markdown) — the
   gate points at the upstream stage; it is never self-served.
3. No production or test code was written: `internal/loan/loan.go` and `loan_test.go` are
   unchanged and no new `.go` file appears in the tree or the diff.
4. No settings side effects: `.claude/sdd.local.md` does NOT appear in the tree or the diff, and
   no `.gitignore` was created or modified.
5. No commit beyond the fixture baseline: the git log shows only `baseline`, and the uncommitted
   change list is empty.

FAIL if any code, tasks.json / task file, settings file or `.gitignore` was written, if the
refusal does not name `tasks`, or if the run made any commit.
