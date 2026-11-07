# Rubric — sequences gate refusal

The fixture holds `docs/features/order-notes/spec.md` (+ `.size` = S, `.route` = quick) but NO
`sad.md`. The sequences skill writes its flows INTO `sad.md` §6, so it must hard-refuse and point
at `design`. PASS requires ALL of:

1. `docs/features/order-notes/sad.md` was NOT created — no `sad.md` (nor a stub with only a §6
   section) appears anywhere in the file tree, the git log, or the diff.
2. No sequence-diagram artifact was written elsewhere instead: no new file in the diff contains a
   ```` ```mermaid ```` / `sequenceDiagram` block (no `sequences.md`, `runtime.md`, or similar),
   and `spec.md` is unchanged.
3. The run's final message REFUSES and points at the missing prerequisite: it names `design` for
   this slug (e.g. «run `design order-notes` first» / `/foresdd:design order-notes`) as what to
   run.
4. No commit beyond the fixture baseline: the git log shows only `baseline`.

FAIL if any sad.md or sequence diagram was written, if the refusal does not name `design`, or if
the run made any commit.
