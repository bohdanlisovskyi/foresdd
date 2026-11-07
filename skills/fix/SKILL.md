---
name: fix
model: inherit
effort: high
agents: [explorer]
description: >
  Use to fix a reported bug spec-first: reproduce it, trace the symptom to the owning feature's
  acceptance criteria, pin it with a failing (RED) test, apply the minimal GREEN fix through the
  same per-task gate implement uses, then patch the spec so the bug class can't silently return.
  Triggers on "fix {bug}", "fix the bug in {slug}", "bug in {feature}", "/foresdd:fix {slug}",
  "regression in {slug}". Triage is three-way: AC exists and is violated (regression) / AC is
  ambiguous (spec-bug — patch the wording) / no AC covers it (gap — add one, marked added-by-fix).
  Works on a repo with no specs at all (soft mode — code-first, recommends survey after). Writes a
  fix record under docs/features/{slug}/_fixes/ and commits the fix (SDD-Fix trailer), the record
  and any spec patch as separate commits.
---

# Skill: fix

The **bugfix entry point** — the backbone in miniature, sized for «it's broken», not «build a feature». A bug is treated as **evidence about the spec**, not only about the code: either an acceptance criterion is violated (the code regressed), the AC was ambiguous enough to permit the behaviour (the spec is the root cause), or nothing covers it (a gap). So the fix always lands in two places — the **code** (RED → GREEN through the same gate `implement` runs) and the **spec** (a surgical AC patch) — tied together by a small fix record.

This skill keeps only its own machinery. Question phrasing → [`../allocations/style.md`](../allocations/style.md); RED-classification semantics → [`../implement/references/tdd-loop.md`](../implement/references/tdd-loop.md) (reused, never duplicated); dispatch policy → [`../allocations/agent-roster.md`](../allocations/agent-roster.md).

## Owner

The engineer on the bug (drives). PM / Tech Lead is consulted only when triage lands on «spec-bug» or «gap» — changing an AC is a product decision, not a code one.

## Inputs

- `<slug>` — optional; pass it when you know which feature owns the bug, otherwise step 2 finds it from the symptom.
- The bug report, in any form — a sentence, a stack trace, a failing request, a screenshot description.
- **Or a review finding.** Invoked from `review`'s *Fix now → fix* (the user names the finding, or there is exactly one open `→ fix` row in the latest `_review/review-*.md`): the finding's headline + `file:line` + AC **is** the bug report. Intake asks nothing it already says, step 2 starts from the cited AC (the recurrence check still runs), and the record's `from_review:` points at the review file.
- **Soft gate (never hard-refuse):** `docs/features/` with ≥1 `spec.md`. Absent (a brownfield repo that never ran the backbone) → still run, in **no-spec mode**: steps 1 → 3 → 4 → record, skip the spec patch, and recommend `/foresdd:survey` in the handoff.
- (Optional) `.claude/sdd.local.md` — gate command overrides; otherwise the commands are detected per `implement`'s cascade.

No depth dial and no `.size` here — a fix is one size, and the interview is the bug report itself.

## Protocol

1. **Intake — reproduce before touching anything.** At most 1–2 `AskUserQuestion` (phrasing per [`../allocations/style.md`](../allocations/style.md)), only for what the report doesn't already say: expected vs actual, the steps, the scope (one user? all? since when?). Outcome: a one-line reproduction statement — «doing X, expected Y, got Z». A bug you can't state this way isn't ready to fix.
   - **Can't reproduce** (the steps run clean, or the report is too thin to try) → don't guess-fix. One `AskUserQuestion`, stating what was tried: **Add details** (the user supplies the missing input/environment/data — retry once) / **Record as unreproduced** (write the record with `triage: unreproduced` — what was tried, the conditions that might matter, and the instrumentation to add as a follow-up; commit only the record, no code) / **Stop** (nothing written).
2. **Trace to spec (triage).** Grep `docs/features/*/spec.md` (+ the candidate slug's `_fixes/` for a recurrence) for the reproduction's domain terms; locate the owning slug and the closest §5 AC. In parallel, dispatch [`explorer`](../../agents/explorer.md) — `subagent_type: "foresdd:explorer"` (fallback `Explore` / inline per [`../allocations/agent-roster.md`](../allocations/agent-roster.md)) — to localize the code path. Three outcomes (decision table → [`./references/triage.md`](./references/triage.md)):
   - **(a) Regression** — an AC describes the expected behaviour and the code violates it. The spec is right; only the code changes.
   - **(b) Spec-bug** — the AC exists but a reasonable implementer could read it and produce the observed behaviour. The wording is the root cause — the AC gets patched (with the user, step 5).
   - **(c) Gap** — no AC covers the behaviour. A new AC is added to §5, marked `<!-- added-by-fix: <date> -->`.
   - **No-spec mode** — no `docs/features/` (or no spec plausibly owns the symptom): skip the spec patch, say so in the record, recommend `survey`.
3. **RED — pin the bug with a failing test.** Write the **minimal** test that reproduces the bug at the level the behaviour implies (unit for a rule, integration for a dependency behaviour, e2e for a flow). Run it and classify the first run per [`../implement/references/tdd-loop.md`](../implement/references/tdd-loop.md) — it must be a **GOOD red** (fails on the assertion that encodes the *expected* behaviour); quote the failing line. A bug that can't be pinned at the first level tried → **go one level up** (unit → integration → e2e) before giving up. Still unpinnable (timing-only, external system you can't fake, production-only data) → one `AskUserQuestion`: **Pin with a scripted manual reproduction** (a runnable script/steps in the record replace the test; the self-check is reported `degraded: no automated pin` and lands in *Needs your attention*) / **Record and stop** (the record holds the reproduction + why it can't be pinned; no code change) — never fix silently without a pin.
   - **Checkpoint — before any production code.** One `AskUserQuestion` that shows, in ≤6 lines: the reproduction statement, the triage branch, the root cause (`file:line`), the quoted RED line, the planned fix in one sentence, and — on (b)/(c) — the proposed AC wording **before → after**. Options: **Proceed (Recommended)** / **Different fix** (the user names the direction; re-plan, ask again) / **Different spec wording** (spec-bug/gap only; the user edits the AC text) / **Stop** (keep the RED test uncommitted, write the record with the follow-up). This one answer is also the spec-change confirmation step 5 needs — step 5 asks again only if GREEN forced a different wording.
4. **GREEN + GATE — minimal fix.** Make the RED test pass with the smallest change; **no drive-by refactors** (anything the fix exposes goes to the record's follow-ups). Then the same per-task gate `implement` runs: unit + lint + vet (+ integration when available), via the detected commands (detection cascade → [`../implement/references/command-detection.md`](../implement/references/command-detection.md)). Red gate → fix it, never commit around it.
5. **Spec patch + fix record.** Apply the step-2 branch — (a) nothing to patch, re-verify the AC; (b) patch the AC wording; (c) add the new AC with the marker. **Any spec change is confirmed with the user** — already done at the step-3 checkpoint; re-ask (before/after shown) only when the applied wording differs from what was confirmed. Then write `docs/features/<slug>/_fixes/<date>-<short-slug>.md` from [`./templates/fix-record.md`](./templates/fix-record.md): symptom → root cause → the pinning test → the spec patch (or why there is none).
6. **Commit + handoff.** With the GATE green (this skill's structural self-check), commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — separate commits: the code fix + its pinning test as `fix: <slug> <short summary>` with trailers `SDD-Fix: <date>-<short-slug>` and `SDD-AC: <id>` (when an AC was traced); the record as `fix: <slug> record <date>-<short-slug>`; the spec patch (if any) as `fix: <slug> spec.md <AC id>`. A red gate → no commits. Then **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) (utility variant — `/clear` optional): *What I did* (incl. the commits with short SHAs) + *Review* (the diff, `_fixes/<date>-<short-slug>.md`, the spec patch if any) + *Run next*: concrete, never «resume what you were doing» — **from a review finding** → the next open `→ fix` finding of that review (`/foresdd:fix <slug>`), or `/foresdd:review <slug>` (delta) when it was the last one; **otherwise** → the backbone stage read off the trail (the first stage not yet `✓`/`↷`, e.g. `/foresdd:ship <slug>` when the feature had already passed review — which then flags its review as stale), or «nothing to resume» when the slug's pipeline is done. **When the fix touched >5 files or crossed a module boundary, also recommend `/foresdd:review <slug>`** — a recommendation, not a gate.

## Definition of Done

- The bug is reproduced by a test that **failed before the fix and passes after** — GOOD red proven, failing line quoted. The only exceptions are the two the user chose explicitly: a scripted manual pin (self-check `degraded`) or `unreproduced` (record only, no code change).
- The gate is clean: unit + lint + vet (+ integration where available).
- The triage outcome is explicit — regression / spec-bug / gap / no-spec / unreproduced — and the matching spec patch is applied (or its absence explained in the record).
- The user confirmed the root cause + planned fix (+ any AC wording) at the step-3 checkpoint before production code was written.
- `docs/features/<slug>/_fixes/<date>-<short-slug>.md` exists: symptom, root cause, the test, the spec patch, follow-ups.
- The commit carries the `SDD-Fix:` trailer (+ `SDD-AC:` when traced); any spec change was user-confirmed.
- The RED-pin (failing test first) + the per-task GATE are this skill's **structural self-check** ([`../allocations/self-check.md`](../allocations/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **Fixing without a pinning test.** «It works now» with no RED proof is a guess that re-breaks silently — the exact failure mode this skill exists to stop.
- **Patching code when the spec was the bug.** If the AC permitted the behaviour, the wording is the root cause; leave it unpatched and the next implementation reintroduces the bug legally.
- **Silent spec edits.** Every AC patch/addition is confirmed with the user — the spec is a contract, not a scratchpad.
- **Drive-by refactoring.** The fix commit is minimal; refactors the fix exposed go to the record's follow-ups, not into the same diff.
- **Skipping the gate because the change is «one line».** One-line fixes break suites just fine.
- **Writing production code before the checkpoint.** The user confirms the root cause and the plan once — a wrong diagnosis caught there costs one question, caught after GREEN costs the whole fix.
- **Guess-fixing a bug you couldn't reproduce.** Record it as `unreproduced` with what was tried; a speculative patch hides the bug, it doesn't fix it.
- **Hard-refusing on a repo without specs.** A brownfield bug is this skill's front door — degrade to no-spec mode and recommend `survey`, never block.
- **Writing a parallel test when `_fixes/` shows the same symptom was fixed before.** That's a recurrence — read the old record and **strengthen its test** instead.

## References & template

- [`./references/triage.md`](./references/triage.md) — the symptom→spec trace: grep strategy, the regression / spec-bug / gap decision table, the `added-by-fix` marker, no-spec mode, the recurrence check.
- [`./templates/fix-record.md`](./templates/fix-record.md) — the fix-record scaffold (symptom → root cause → pinning test → spec patch → follow-ups).
- [`../implement/references/tdd-loop.md`](../implement/references/tdd-loop.md) — RED classification (GOOD red / BAD red / false-pass) — the semantics step 3 reuses.
- [`../implement/references/command-detection.md`](../implement/references/command-detection.md) — how the step-4 gate commands are resolved (settings override → Makefile → package scripts → language manifests).
- [`../allocations/style.md`](../allocations/style.md) · [`../allocations/agent-roster.md`](../allocations/agent-roster.md) · [`../allocations/handover.md`](../allocations/handover.md).

## Example invocation

> **User:** «/foresdd:fix — discounts are applied twice when the user clicks pay twice fast»
> **Skill:** intake confirms: expected one discount per order, got two on a double-click (all users, since the checkout-discounts release). Trace: `docs/features/checkout-discounts/spec.md` AC-04 says «a discount is applied to an order at most once» → the code violates it → **regression**. `explorer` localizes the apply-discount handler (no idempotency check). RED: an integration test posting the same apply twice asserts one discount row — fails with `got 2, want 1` (GOOD red). Checkpoint: «regression of AC-04 · root cause `discounts/apply.go:41` no idempotency check · fix: guard on the existing uniqueness key» → *Proceed*. GREEN: guard on the existing uniqueness key; gate clean. Spec: nothing to patch (AC-04 was right). Record `_fixes/2026-06-12-double-discount.md`; commit `fix: checkout-discounts double-applied discount` + `SDD-Fix:` / `SDD-AC: AC-04` trailers. Handoff: 2 files touched → no review push; resume.
