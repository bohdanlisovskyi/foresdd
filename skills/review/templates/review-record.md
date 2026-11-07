---
slug: <slug>
date: <YYYY-MM-DD>
mode: <full | delta>        # delta = re-review of the surface changed since `previous`
previous: <none | review-<date>.md>
base: <base ref>..<head short sha>
route: <quick | standard | full>   # from .route (missing → standard, say so)
gate: <pending | PASS | CHANGES REQUESTED>
---

# Review: <slug> — <date>

<!-- instruction: created BEFORE the first resolution question (gate: pending) and appended after
EACH resolution — never written all at the end. Scope + trace are filled at creation; findings
grow one row at a time; the verdict is set last. -->

## Scope

<!-- `git diff --stat <base>..HEAD` summary (files / +/-), the SDD-AC trailers the diff claims, and
for a delta review: the commits since `previous` + which earlier findings this re-checks. -->

## Trace

<!-- The end-to-end chain the reviewer walked, one row per §5 AC (incl. added-by-fix ones). A link
whose stage was legitimately skipped for this route is `N/A (<reason>)`, NOT a gap — e.g.
`N/A (data-model: no schema change)`. A `—` is a real gap and must appear as a stage-1 finding. -->

| AC | §6 flow | data-model | api | task | test | code |
|---|---|---|---|---|---|---|
| AC-01 | <flow/branch> | <entity or N/A (…)> | <op or N/A (…)> | <task id> | <test name> | <file:line> |

## Findings

<!-- One row per finding, appended the moment it is resolved. Severity per the reviewer report
(stage-1 = blocker; stage-2 = major | minor). Resolution = Fix now (→ fix | implement) / Defer
(spec §8 row: owner + due) / Not an issue (why). -->

| # | Stage · severity | Headline (the consequence) | file:line | AC | Resolution |
|---|---|---|---|---|---|
| 1 | stage-1 · blocker | <…> | <…> | AC-NN | Fix now → `/foresdd:fix <slug>` |

## Verdict

<!-- PASS — no open finding of any stage (every Fix-now landed and was delta-reviewed, or the
review found nothing), every Defer has owner + due. CHANGES REQUESTED — at least one Fix-now is
still outstanding. One line on why, plus the next command. -->
