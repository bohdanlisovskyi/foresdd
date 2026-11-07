# Rubric — plan-tests gate refusal

The fixture holds `docs/features/bulk-export/.size` (= M) and `.route` (= standard) but NO
`spec.md`. A test plan maps spec §5 acceptance criteria to tests, so without the spec there is
nothing to map — plan-tests must hard-refuse and point at `specify`. PASS requires ALL of:

1. `docs/features/bulk-export/test-plan.md` was NOT created — no `test-plan.md` appears anywhere
   in the file tree, the git log, or the diff.
2. The run did NOT create `docs/features/bulk-export/spec.md` (neither a stub spec nor one
   carrying an inline test plan) — the gate points at the upstream stage; it is never
   self-served. No AC→test table appears in any file in the diff.
3. The run's final message REFUSES and points at the missing prerequisite: it names `specify`
   for this slug (e.g. «run `specify bulk-export` first» / `/foresdd:specify bulk-export`) as
   what to run.
4. No commit beyond the fixture baseline: the git log shows only `baseline`.

FAIL if a test-plan.md or spec.md was written, if the refusal does not name `specify`, or if the
run made any commit.
