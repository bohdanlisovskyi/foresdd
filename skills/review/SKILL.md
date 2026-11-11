---
name: review
model: inherit
effort: high
agents: [reviewer]
description: >
  Use to run an independent, clean-context code review of an implemented feature against its spec
  and acceptance criteria before shipping. Triggers on "review {slug}", "code review the changes
  for {slug}", "review the diff for {slug}", "is {slug} ready to ship", "/foresdd:review {slug}".
  Dispatches the reviewer subagent over the whole feature diff (stage 1 spec/AC compliance, stage
  2 quality), collects cited findings, and resolves each with you. Hard-refuses if the feature
  isn't implemented yet.
---

# Skill: review

The independent review gate. After `implement` has written + tested + committed the code, `review` looks at the **whole change at once, with fresh eyes** — does it actually satisfy every acceptance criterion, and is it good code? This is distinct from the per-task gate inside `implement` (which proves each task green): `review` is the cross-cutting, clean-context pass a human reviewer would do on the PR.

It reuses the shared clean-context discipline ([`../allocations/critic.md`](../allocations/critic.md)) and the [`reviewer`](../../agents/reviewer.md) subagent (read-only). Question phrasing per [`../allocations/style.md`](../allocations/style.md).

## Owner

Tech Lead / a reviewer who did **not** write the code (independence is the point).

## Inputs

- `<slug>` — feature slug.
- `--delta` — optional; re-review only the surface changed since the latest `_review/review-*.md` (auto-selected when that record says `CHANGES REQUESTED` — see step 1).
- **Gate (hard refuse):** an implemented change must exist (commits on the feature branch, or a non-empty working diff). Nothing to review → «run `implement <slug>` first».
- Read for the review baseline — the **whole AC chain**, so the trace can be checked end-to-end: `docs/features/<slug>/spec.md` §5 (the full AC set — the source of truth, not the diff's trailers), `sad.md` §6 (the sequence flows/branches each AC should appear in), `data-model.md` / `contracts/openapi.yaml` / Accepted `adr/` (the contracts the code must honour), `test-plan.md` (the AC→test map, if a separate file), and `tasks.json` (which AC each task claimed).
- When `spec.md` frontmatter has `extends: <area>`: `docs/features/<area>/spec.md` — the baseline. Stage 1 also checks that every baseline AC **not** named in a change AC's `supersedes` still holds in the touched code (its §9 anchor is the starting point); a silent change to observed behaviour is a stage-1 finding.
- `docs/features/<slug>/.route` (missing → `standard`, say so) — decides which links of the chain are legitimately absent; see step 1.

## Protocol

1. **Scope the diff + the chain.** Determine the change under review: `git diff <base>..HEAD` on the feature branch (base = `git merge-base HEAD <default branch>`), or the named changed files. Note the `SDD-AC` trailers — the ACs the implementation claims to satisfy. Then:
   - **Mode.** The latest `_review/review-*.md` says `CHANGES REQUESTED` (or `--delta` was passed) → **delta mode**: the diff is `<that record's head>..HEAD`, and the reviewer re-checks (i) every finding marked *Fix now* in that record and (ii) the newly changed lines; the full end-to-end trace re-runs only for the ACs those changes touch. Otherwise → **full mode**. State the mode in one line.
   - **Legitimately absent links.** For each optional artifact that doesn't exist (`ux-flows.md`, `sad.md` §6 sequences, `data-model.md`, `contracts/openapi.yaml`, `screens.md`, a separate `test-plan.md`), check its N/A condition in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) (the fast-lane table). Condition holds → that link is **`N/A (<reason>)`** for the whole trace, and the list goes to the reviewer in its dispatch prompt. Condition does **not** hold (e.g. the diff adds a migration but there is no `data-model.md`) → that missing artifact is itself a **stage-1 finding**. The route only decides who skipped it; the N/A condition decides whether skipping was legal.
2. **Dispatch the independent reviewer.** Run the [`reviewer`](../../agents/reviewer.md) agent — `subagent_type: "foresdd:reviewer"` (read-only, **clean context** — it re-reads spec/contracts itself, no paraphrase; **model per `judgment_model`; effort `xhigh` on L/XL** via `CLAUDE_CODE_EFFORT_LEVEL`, per [`../allocations/agent-roster.md`](../allocations/agent-roster.md)) — over the diff along the dimensions in [`./references/review-dimensions.md`](./references/review-dimensions.md): **stage 1** — every claimed AC genuinely satisfied **and the whole §4 user-story set + §5 AC set traced end-to-end (spec → sequences §6 → data-model → api → tasks → implement): every §4 user story has ≥1 AC and a §6 flow, and every §5 AC reaches code+test — spanning every surface declared in `sad.md` `target_surfaces` (a UI AC traces to a component / e2e-through-UI test, not only a backend one) — flagging any user story or AC that dropped out anywhere in the chain, not only the ACs the diff claims via its `SDD-AC` trailers**; **stage 2** — conventions, error/edge handling, security, boundary violations, test adequacy. Links marked `N/A` in step 1 are passed in and are **not** gaps. For a large diff, fan out one reviewer per dimension and merge.
3. **Collect cited findings.** Each finding cites `file:line` + the AC/contract it touches. Drop uncited findings (per the critic discipline). A clean review returns `REVIEW_CLEAN`. If the reviewer ran asynchronously and came back as an idle/completion signal with no report, **pull the full report through the host's messaging channel** — never accept a verdict without its text (→ [`../allocations/agent-roster.md`](../allocations/agent-roster.md), shared-contract point 2).
4. **Show the overview first.** Before any question, create `docs/features/<slug>/_review/review-<date>.md` from [`./templates/review-record.md`](./templates/review-record.md) (scope, mode, the trace table, findings empty, gate `pending`). Then print **one overview table** of every finding — `# · stage · severity · headline (the consequence) · file:line · AC` — in the reviewer's order (stage-1 blockers, stage-2 major, stage-2 minor), headed by its tally line («3 stage-1 · 5 stage-2 (2 major, 3 minor)»). The user sees how big the job is before deciding anything. `REVIEW_CLEAN` → skip to step 6 with `PASS`.
5. **Resolve — stage-1 one at a time, stage-2 in batches — writing as you go.** Phrasing per [`../allocations/style.md`](../allocations/style.md). After **each** answer, append that finding with its resolution to the record — and on Defer write the spec §8 row — immediately, never all at the end ([`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) §1).
   - **Stage-1 (blockers)** — one `AskUserQuestion` each, quoting the AC and the gap: **Fix now** / **Defer = de-scope** (an explicit spec change: the AC moves to §8 Open questions with owner + due — the owner, not the reviewer, decides) / **Not an issue** (the reviewer misread; record why).
   - **Stage-2** — up to **4 findings per `AskUserQuestion` call** (one question each, majors first), options **Fix now** / **Defer** / **Not an issue**. Before the first stage-2 batch, offer one shortcut question when there are >4 stage-2 findings: **Resolve individually** / **Fix all majors, defer all minors** / **Defer all stage-2** — a shortcut still writes one record row per finding.
   - **Where *Fix now* goes.** A finding that is **localized** (one behaviour, ≤ ~3 files, no new task-sized work — a missing guard, a wrong status code, an untested branch) → route to **`/foresdd:fix <slug>`**, which pins it with a RED test and applies the minimal fix through the per-task gate; record `Fix now → fix`. A finding that needs **new task-sized work** (a missing AC implementation, a new endpoint/screen, a cross-module change) → `/foresdd:implement <slug>` as a follow-up task; record `Fix now → implement`.
6. **Set the verdict.** **`PASS`** — no finding is resolved *Fix now* (all were deferred-with-owner, dismissed-with-reason, or there were none). **`CHANGES REQUESTED`** — at least one *Fix now* is outstanding, whatever its stage. Write it into the record's `gate:` and *Verdict*. A stage-1 finding can never end as an unexplained open item — it is Fix now, an explicit de-scope, or Not an issue with the reason.
7. **Commit** per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — one commit per document: `review: <slug> review-<date>.md`; `review: <slug> spec.md deferred findings` only when a Defer changed `spec.md` (otherwise `git status` is empty and the commit is skipped).
8. **Verdict + next.** Then **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) — *What I did* (mode full/delta, the tally, the commits with short SHAs) + *Review* (`_review/review-<date>.md`) + *Run next*: `PASS` → (`/clear`, then `/foresdd:ship <slug>`); `CHANGES REQUESTED` → **no `/clear`** (stay in context to iterate) — list the Fix-now findings in *Needs your attention*, grouped by where they go: `/foresdd:fix <slug>` once per `→ fix` finding, `/foresdd:implement <slug>` for the `→ implement` ones — then `/foresdd:review <slug>` again, which picks **delta mode** automatically.

## Definition of Done

- The independent reviewer ran over the whole feature diff (not just per-task).
- Every claimed AC was checked for genuine satisfaction; **the whole §4 user-story set + §5 AC set was traced end-to-end (spec → sequences → data-model → api → tasks → implement)** — every §4 US has ≥1 AC and a §6 flow, every §5 AC reaches code+test — and anything that dropped out anywhere in the chain was flagged, not just the ACs the diff claims. Every in-scope user story / AC is covered or explicitly deferred with owner + due.
- The user saw the overview table before the first resolution question; stage-2 findings were batched (≤4 per call).
- Every finding is resolved (Fix now → fix/implement / deferred with owner + due / dismissed-with-reason); no stage-1 finding is left unexplained.
- Every missing optional artifact was checked against its N/A condition: legal skips are `N/A (<reason>)` in the trace, illegal ones are stage-1 findings.
- A review record exists (from the template) with mode, trace, findings and a `PASS` / `CHANGES REQUESTED` verdict that follows the step-6 rule.
- The clean-context reviewer pass (the whole skill is a verifier) is this skill's **structural self-check** ([`../allocations/self-check.md`](../allocations/self-check.md)); the verdict is its report.

## Anti-patterns

- **Reviewing your own code in the same context that wrote it.** The reviewer must be clean-context and, ideally, not the author — that's what catches the blind spots.
- **Uncited findings.** «This feels off» is not actionable — cite `file:line` + the AC/contract or drop it.
- **Shipping with an open AC finding.** A stage-1 gap means the feature doesn't do what the spec says — fix or explicitly de-scope (spec change), never wave through.
- **Under-checking `added-by-fix` ACs.** An AC that entered §5 through a bug is proof the spec already missed that case once — trace it at least as strictly as the rest; the fix's pinning test is its floor, not proof of full coverage.
- **Trusting the diff's `SDD-AC` trailers as the complete AC set.** The trailers only list what the diff *claims*. Review traces the **whole** §5 set end-to-end — an AC that never reached the diff (no task wrote it, no test asserts it) is the most dangerous gap precisely because the trailers can't reveal it.
- **Re-litigating style the repo already settled.** Judge against the conventions + contracts, not personal taste.
- **Flagging a legitimately skipped artifact as a gap.** A `quick` XS with no schema change has no `data-model.md` by design — that link is `N/A`, not a finding. The N/A condition decides, not the file's absence.
- **One question per minor finding.** Ten nit-level questions bury the one blocker; show the overview, batch stage-2.
- **Re-reviewing the whole feature after a one-line fix.** After `CHANGES REQUESTED`, the next run is a delta review of what changed plus the earlier Fix-now findings.
- **Treating the per-task gate as the review.** Green tests prove each task; they don't prove the change coheres or that the AC are truly met end-to-end.

## References & template

- [`./references/review-dimensions.md`](./references/review-dimensions.md) — the review dimensions + the reviewer dispatch shape.
- [`./templates/review-record.md`](./templates/review-record.md) — the review-record scaffold (scope, mode, trace table, findings, verdict).
- [`../allocations/critic.md`](../allocations/critic.md) — the clean-context dispatch discipline this reuses.
- [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) — the N/A conditions that decide which chain links are legitimately absent.

## Example invocation

> **User:** «/foresdd:review checkout-discounts»
> **Skill:** full mode (no earlier record); `git diff main...HEAD` — 9 files, claims AC-01..AC-05. Route `quick`: `data-model.md` absent, the diff has no migration → `N/A (no schema change)`; `screens.md` absent, `target_surfaces: [backend-api]` → `N/A (no UI surface)`. Reviewer: «2 stage-1 · 4 stage-2 (1 major, 3 minor)». Overview table shown. Stage-1 #1 «AC-05 has no test — expiry can silently stop working» → *Fix now → fix*; #2 «AC-02 says 'per order', code applies per cart» → *Not an issue* (cart = order in this domain, CONTEXT.md). Stage-2 batch of 4 → major fixed now (→ fix), minors deferred. Verdict `CHANGES REQUESTED`. Handoff: `/foresdd:fix checkout-discounts` ×2, then `/foresdd:review checkout-discounts` (→ delta mode).
