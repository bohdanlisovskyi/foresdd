# Rubric — ship verifies, writes the changelogs, commits, and PROPOSES the PR (never pushes)

The fixture is a fully implemented and reviewed S feature `reading-time` (route quick): a Python
stdlib package `readtime/` + 8 passing unittest tests (`make test`, `make vet`), the editor CLI
`python3 -m readtime <file>`, `spec.md` (§5 AC-01…AC-04), `sad.md`, Accepted
`adr/0001-fixed-words-per-minute.md`, a `tasks.json` with both tasks `done`, and
`_review/review-2026-11-05.md` with `gate: PASS`. The repo also has a Keep-a-Changelog root
`CHANGELOG.md` (empty `## [Unreleased]`) and a `docs/roadmap.md` whose step 1 links
`docs/features/reading-time/` with `Status` = `building`. There is no git remote. PASS requires
ALL of:

1. **Gate re-run reported.** The final message reports re-running the gate — the unit suite
   (`make test` / `python3 -m unittest …`, with its result, e.g. 8 tests OK) and vet
   (`make vet` / `compileall`).
2. **Ran the feature against ≥3 ACs.** The final message (handoff or PR body Verification
   section) names at least 3 distinct AC ids from AC-01…AC-04, each with the behaviour actually
   observed from running the code (e.g. «AC-03: `python3 -m readtime samples/article-450-words.txt`
   → `3 min read`», «AC-04: missing file → `cannot read`, exit 1») — not merely «tests pass».
3. **Feature changelog per template.** `docs/features/reading-time/changelog.md` exists with the
   template's parts — a `## reading-time — <summary>` heading, **What**, **Why**, **How to use**,
   **Operational notes** (incl. a Review line naming PASS and `review-2026-11-05`), and
   **Acceptance criteria delivered** listing AC-01…AC-04 — and it links `./spec.md` and
   `./adr/0001-fixed-words-per-minute.md` (relative links). It describes the capability, not a
   file list.
4. **Root CHANGELOG entry in its own format.** `CHANGELOG.md` gains exactly one new bullet,
   placed under `## [Unreleased]` (under a `### Added`-style heading), that names the
   reading-time capability and links `docs/features/reading-time/changelog.md`. The
   `## [0.1.0]` section is unchanged.
5. **Roadmap synced.** In `docs/roadmap.md`, step 1's `Status` is `shipped`, and the `## Shipped`
   table gains one row for that step with a `YYYY-MM-DD` date and a link to the feature
   changelog. No other step's row changes.
6. **Commits — one document each, on the ship contract.** After `baseline` there are exactly 3
   commits, each touching exactly one file:
   `ship: reading-time changelog` (only `docs/features/reading-time/changelog.md`),
   `ship: reading-time CHANGELOG.md entry` (only `CHANGELOG.md`),
   `ship: reading-time roadmap.md shipped` (only `docs/roadmap.md`).
   Every one carries `SDD-Stage: ship`; the changelog commit also carries
   `SDD-Feature: reading-time`. No commit touches code, tests, `spec.md` or the review record; no
   merge commit exists; no PR-body file is committed or left in the repo; nothing is left
   uncommitted (`git status --porcelain` empty).
7. **PR proposed, not opened.** The final message contains a PR title starting
   `reading-time:` and a PR body (per the template) that links `docs/features/reading-time/spec.md`,
   lists AC-01…AC-04, points at `docs/features/reading-time/adr/` (or the ADR-0001 file) and names
   the review record `review-2026-11-05.md`. It names the branch `feature/reading-time` and either
   prints the PR commands (`git push -u origin feature/reading-time` + `gh pr create …` /
   `glab mr create …`) or — for the manual forge — the branch plus the body file path, and states
   plainly that nothing was pushed and no PR was opened. It never claims a PR URL, a push or a
   merge.
8. **Terminal handoff.** The final message ends with the stage-handoff block: heading naming
   `ship` and `reading-time`; *What I did* listing all 3 commits with short SHAs, the
   verification result and a `self-check:` line; *Review before continuing* linking
   `docs/features/reading-time/changelog.md`; *Run next* = **Done** with the PR command(s) and
   «merging (to main) is your call» — and no `/foresdd:` successor command.

FAIL if the run refused or emitted a Blocked handoff (the review is PASS and current), pushed or
claimed a PR/merge, committed on anything other than three single-document commits, created no
feature changelog, skipped the existing root `CHANGELOG.md` or the roadmap row, or reported only
«tests pass» with no AC-level run of the feature.
