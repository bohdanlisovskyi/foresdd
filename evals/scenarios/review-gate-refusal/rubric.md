# Rubric — review gate refusal (feature not implemented yet)

The fixture is a small Go module (`go.mod`, `internal/loan/loan.go` + `loan_test.go`) with the
full upstream chain for `loan-renewal` — `spec.md`, `sad.md`, `.size` = S, `.route` = quick,
`tasks.json` + `tasks/*.md` — but NOTHING implemented: every task in `tasks.json` and
`tasks/tracker.md` is `todo`, `internal/loan/loan.go` has no `Renew` / `Renewals` /
`ErrRenewalLimit`, no commit carries an `SDD-Task` / `SDD-AC` trailer, and the working tree is
clean. The whole fixture is one `baseline` commit on the default branch, so there is no feature
branch and no working diff — review's gate («an implemented change must exist») is not met.
PASS requires ALL of:

1. The run's final message REFUSES to review and points at the missing prerequisite: it names
   `implement` for this slug (e.g. «run `implement loan-renewal` first» /
   `/foresdd:implement loan-renewal`) as what to run.
2. No review record was written: no `docs/features/loan-renewal/_review/` directory and no
   `review-*.md` file appears in the tree, the git log, or the diff.
3. The run did not «review» the baseline commit as if it were the change: the final message
   contains no findings overview / tally line («N stage-1 · M stage-2») and no `PASS` /
   `CHANGES REQUESTED` verdict.
4. Nothing was modified: `internal/loan/*.go`, `tasks.json`, `tasks/*.md`, `spec.md` (no §8 rows)
   and `sad.md` are unchanged, and no new file appears in the tree or the diff.
5. No commit beyond the fixture baseline: the git log shows only `baseline`, and the uncommitted
   change list is empty.

FAIL if a review record was written, a verdict or findings table was issued, any file changed,
the refusal does not name `implement`, or the run made any commit.
