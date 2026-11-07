---
name: ship
model: inherit
effort: medium
agents: []
description: >
  Use to close the loop after review — verify the feature actually works, write the changelog /
  knowledge-base note, and open the pull request. Triggers on "ship {slug}", "open a PR for
  {slug}", "changelog for {slug}", "prepare {slug} for merge", "/foresdd:ship {slug}". Re-runs the
  gate, runs the app/feature to confirm the spec's outcomes for real (not just green tests),
  drafts a changelog + PR body that link spec/ AC/ADRs, and proposes the PR command for whatever
  forge the repo uses. Never auto-merges to main.
---

# Skill: ship

The closing step. `review` confirmed the change is correct on paper; `ship` confirms it **works in reality** and packages it for merge. The loop ends here: a reviewed, verified change with a changelog and an open PR — not a merge to main (that stays a human decision).

Forge-agnostic and stack-agnostic: the verification commands are detected the way `implement` detects them; the PR step targets whatever forge the remote points at (GitHub via `gh`, GitLab via `glab`, or copy-paste).

## Owner

The implementer (drives) + the reviewer who signed off in `review`.

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** the latest `docs/features/<slug>/_review/review-*.md` has `gate: PASS`. No record → «run `/foresdd:review <slug>` first»; latest is `CHANGES REQUESTED` → «the Fix-now findings are still open — run the fixes, then `/foresdd:review <slug>` (delta)». Either way emit the **Blocked** handoff.
  - **Explicit override only.** The user may say «ship without review» / pass `--skip-review` (e.g. a hotfix). Then proceed, but put «⚠ shipped without a PASS review» in *Needs your attention*, the changelog's operational notes and the PR body's Verification section. Never infer the override.
- Read: `spec.md` (what to claim in the changelog), Accepted `adr/` (decisions worth recording), the latest `_review/review-*.md` and any `_fixes/*.md` (linked from the PR), `.route` / `.size`, the feature's commits (the `SDD-Task` / `SDD-Fix` history).

## Protocol

0. **Staleness check — is the review still about this code?** Compare the PASS record's `base:` head SHA with `HEAD`: `git log <review head>..HEAD -- . ':!docs/'`. Commits that touch code after the review → one `AskUserQuestion`: **Delta review first (Recommended)** — stop with the Blocked handoff naming `/foresdd:review <slug>` (it runs delta mode on just those commits) / **Ship anyway** — list the unreviewed commits in *Needs your attention* and the PR body's Verification section. Only `docs/` commits after the review (records, spec §8 rows) → not stale, continue silently.
1. **Final verification — does it actually work.** Re-run the detected gate (unit + integration where available + lint + vet). Then **run the feature for real** against its acceptance criteria — not just "tests pass": start the app / hit the endpoint / exercise the flow and observe the spec's outcomes (e.g. the default-on read returns defaults; an invalid value is rejected). Concretely: **spot-check at least 3 of the most critical §5 AC outcomes** (fewer only if the spec has fewer; scale the count with the feature's breadth), and for each name the AC id + the behaviour actually observed — «AC-03: posted the same apply twice → one discount row» — so the verification is checkable, not a vibe. If the app can't be run here (no runtime, no Docker), say so explicitly and record what was verified vs deferred — never claim verified-working when only tests compiled.
2. **Write the changelog — in two places.**
   - **Feature note (always):** `docs/features/<slug>/changelog.md` from [`./templates/changelog.md`](./templates/changelog.md): what changed, why (link spec + the key ADRs), any migration/operational note (e.g. "adds migration 000023 — run it on deploy"), and how to use it. Partner-facing if the change is partner-facing.
   - **Project changelog (only if it exists):** a repo-root `CHANGELOG.md` (or `CHANGELOG`, `CHANGES.md`) → add **one entry** under its unreleased section, in **its** format (Keep a Changelog `### Added/Changed/Fixed`, a plain bullet list, …) — one line naming the capability + a link to the feature note. No such file → don't create one; say so in *What I did*. A file whose format you can't infer → show the proposed line and ask where it goes.
3. **Update the roadmap.** Edit `docs/roadmap.md` directly (this is the roadmap's `ship` sync hook — don't run the `roadmap` skill): set the step's `Status` to `shipped` and add a **Shipped** row with today's date + the feature-note link (the PR link is added in step 6 once the PR exists). No roadmap, or no row for this slug → skip and say so; it's optional.
4. **Commit before the PR.** Ensure the work is on a feature branch (not the default branch) — on the default branch, stop and ask whether to create `feature/<slug>` from here. Then commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — one commit per document: `ship: <slug> changelog`, `ship: <slug> CHANGELOG.md entry` (only when the root file exists), `ship: <slug> roadmap.md shipped` (skipped when there is no roadmap). These commits land on the feature branch, so the PR carries them.
5. **Prepare the PR.** Draft the title (`<slug>: <the changelog's one-line summary>`) and the body from [`./templates/pr-body.md`](./templates/pr-body.md): summary, the AC it satisfies, links to spec/sad/ADRs, the review record + fix records, the `SDD-Task` / `SDD-Fix` commit list, the test + verification evidence, and any migration/rollback note. Write the body to a temp file **outside the repo** (it is not a committed document).
6. **Detect the forge, ask, then run.** Inspect the remote: `github.com` → `gh`; `gitlab.com`/self-hosted GitLab → `glab`; anything else (or the CLI isn't installed/authenticated — check `gh auth status` / `glab auth status`) → manual. If a PR/MR already exists for the branch (`gh pr view` / `glab mr view`), offer to **update its body** instead of creating a second one. Show the exact commands (`git push -u origin <branch>` + `gh pr create --title … --body-file …` / `glab mr create --title … --description …`) and the title, then **one `AskUserQuestion`**: **Push & open PR (Recommended)** / **Push & open as draft** / **Just print the commands**. On a push choice, run them; on success, add the PR URL to the roadmap's Shipped row, commit (`ship: <slug> roadmap.md PR link`) and push that one commit too. On failure (rejected push, auth error) → show the error, print the commands, mark the handoff `⚠️`. Manual forge → print the branch + the body file path. **Never merge, never push to the default branch, never force-push.**
7. **Summary (terminal handoff).** **Emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) (terminal variant) — *What I did* (verification result: verified-working / what was deferred and why; the changelog(s) written; the roadmap update; the commits with short SHAs; pushed or not) + *Needs your attention* (skip-review override, unreviewed commits, deferred verification — when any) + *Review* (`docs/features/<slug>/changelog.md` + the PR) + *Run next* = **Done**: the PR URL (or the commands, if not run) — merging to main is your call; there is no `/foresdd:` successor.

## Definition of Done

- The latest review record is `PASS` and not stale — or the override / the unreviewed commits are stated in the handoff and the PR.
- The gate was re-run and the feature was exercised against its AC (or the deferral was stated explicitly with the reason).
- `docs/features/<slug>/changelog.md` exists, linking spec + ADRs; the root `CHANGELOG.md` got one entry when it exists; both (and the roadmap update) are committed on the feature branch before the PR.
- A PR body is prepared and the user chose push / draft / print in one question; the PR URL (or the commands) is in the handoff (work on a feature branch; main untouched).
- The run-the-feature verification (real run against the ACs, not just green tests) is this skill's **structural self-check** ([`../allocations/self-check.md`](../allocations/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **"Tests pass" ≠ "it works".** Run the actual feature against the spec's outcomes; green unit tests don't prove the wired system behaves.
- **Claiming verified when you only compiled.** If the runtime/Docker wasn't available, say what was deferred — don't overstate.
- **Auto-merging to main / pushing to a shared remote unasked.** Propose the PR; the merge is the team's call.
- **A changelog that restates the diff.** Say what changed and why (link the spec + ADR), plus the operational note (migrations, flags) — not a file list.
- **Forgetting the migration/rollback note** when the change includes one — the deployer needs it.
- **Shipping on a stale review.** A PASS from before the last code commit reviewed different code — run a delta review or say plainly what went unreviewed.
- **Creating a root `CHANGELOG.md` the repo never had.** Follow the project's conventions; the per-feature note is always enough.
- **Opening a second PR for the same branch.** Check for an existing one first and update its body.

## References & template

- [`./templates/changelog.md`](./templates/changelog.md) — changelog / KB-note scaffold.
- [`./templates/pr-body.md`](./templates/pr-body.md) — PR description scaffold.
- [`../implement/references/command-detection.md`](../implement/references/command-detection.md) — how the step-1 gate commands are resolved.

## Example invocation

> **User:** «/foresdd:ship checkout-discounts»
> **Skill:** latest record `review-2026-06-14.md` = PASS; since its head only `docs/` commits → not stale. Gate green (unit 142 ✓, integration 18 ✓, lint ✓). Ran the service: AC-01 «10% code on a 50.00 order → total 45.00» ✓, AC-03 «expired code → 422 `code_expired`» ✓, AC-04 «apply twice → one discount row» ✓. Wrote `docs/features/checkout-discounts/changelog.md`; root `CHANGELOG.md` is Keep-a-Changelog → one `### Added` line under `[Unreleased]`. Roadmap step 3 → shipped. 3 commits. Remote is github.com, `gh` authenticated, no PR yet → asked: *Push & open PR* → PR #128 opened; roadmap PR link committed + pushed. Handoff: **Done** — #128; merging is your call.
