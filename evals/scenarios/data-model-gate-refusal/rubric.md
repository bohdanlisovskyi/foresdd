# Rubric — data-model gate refusal (sad.md missing, spec.md present)

The fixture holds `docs/features/feedback-reactions/spec.md` (+ `.size` = S, `.route` = quick),
the live `migrations/` tree (`000001_init`, `000002_create_feedback`) and
`docs/architecture-map.md`, but NO `docs/features/feedback-reactions/sad.md`. The spec clearly
introduces a new entity (reaction), so the temptation to design the schema anyway is real.
data-model hard-refuses when either spec.md or sad.md is missing and points at the missing one.
PASS requires ALL of:

1. `docs/features/feedback-reactions/data-model.md` was NOT created (not even the bootstrapped
   template) — it appears nowhere in the file tree, the git log, or the diff.
2. No migration was written: no `docs/features/feedback-reactions/migrations/` directory and no
   `*.up.sql` / `*.down.sql` file appears in the diff; the live `migrations/` tree is unchanged.
3. The run did NOT create `docs/features/feedback-reactions/sad.md` itself (nor any stub of it) —
   the gate points at the upstream stage; it is never self-served.
4. The run's final message REFUSES and points at the MISSING prerequisite specifically: it names
   `design` for this slug (e.g. «run `design feedback-reactions` first» /
   `/foresdd:design feedback-reactions`) as what to run. It does not claim spec.md is missing.
5. No commit beyond the fixture baseline: the git log shows only `baseline`.

FAIL if data-model.md, any migration, or a sad.md was written; if the refusal names only
`specify` (or does not name `design`); or if the run made any commit.
