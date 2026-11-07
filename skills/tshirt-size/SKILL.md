---
name: tshirt-size
model: haiku
effort: low
agents: []
description: >
  Use to T-shirt-size a feature (XS/S/M/L/XL) and write docs/features/{slug}/.size plus the
  pipeline route docs/features/{slug}/.route (quick|standard|full) so later skills know how much
  of each artifact to produce and how handoffs resolve skips. Triggers on "t-shirt size",
  "t-shirt sizing", "tshirt size {slug}", "classify size", "feature size", "is this XS or M for
  {slug}", "size {slug}", "change route", "/foresdd:tshirt-size {slug}". Infers the four signals
  (PR count / time / new module-API-migration / breaking changes) from the idea or spec when it
  can, otherwise asks them in ONE AskUserQuestion call; the highest signal sets the size via the
  shared T-shirt sizing matrix; derives the default route (XS/S→quick, M→standard, L/XL→full);
  confirms size + route in ONE question; and writes the one-line .size and .route files — the
  source of truth; the feature_size: frontmatter mirrors in spec.md and sad.md are re-synced to
  it on every (re)classification.
---

# Skill: tshirt-size

Atomic skill — **T-shirt sizes** a feature into XS/S/M/L/XL and fixes the result in
`docs/features/<slug>/.size`, plus the pipeline **route** (`quick` / `standard` / `full`) in
`docs/features/<slug>/.route`. This is the single source of size- and route-aware behaviour for
the rest of the pipeline: later skills read `.size` to decide MVP vs Full output depth, and
their handoffs read `.route` to decide how optional-stage skips resolve (auto-skip / offered /
never — the Routes table in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md)).

This skill is the **canonical owner of the T-shirt sizing matrix** → [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md). The signal table, the highest-signal-wins rule, the route cheat-sheet, and the MVP-vs-Full table all live there; this skill only runs the dialogue and writes the files.

*(Formerly `classify-size` — the old trigger phrase «classify size» still routes here.)*

**Called inline by `specify`.** When `.size` is absent at the start of the backbone, `specify` step 1 runs this protocol inline (same signals, same files, folded into its bundled question) — this skill stays the standalone utility for sizing up front or **re-sizing when scope changes**; the protocol is never duplicated elsewhere.

## Owner

PM or Tech Lead (driver of the intake phase). An architect may escalate S → M on spotting a new subsystem.

## Inputs

- `<slug>` — feature slug.
- (Optional) evidence to infer signals from — `docs/features/<slug>/spec.md`, an idea brief, or the user's request text. The skill works without any of it (it then asks all four signals).

## Protocol

At most **two** user interactions in the common case: the four signals (skipped when all four are inferred) and the confirm question.

1. **Check existing.** `test -f docs/features/<slug>/.size` (and `.route`). If `.size` exists, read both and ask ONE question: «Currently `<X>` / route `<Y>`. What do you want to change?» — options: `Only the route` (jump to step 4 with the size fixed) / `Re-size` (continue) / `Keep as is` (STOP, nothing written). Switching only the route is a legal, common case — mid-flight override per the Routes table.
2. **Infer the signals.** Read whatever evidence exists (Inputs). For each of the four signals in the matrix pick the answer the evidence supports, with a ≤10-word evidence note («adds `/limits` endpoint → one of three»). Mark a signal *unknown* rather than guess.
3. **Ask the signals — in ONE call.** All four inferred → skip to step 4 (the confirm question shows them, and `Adjust signals` brings this call back). Otherwise one `AskUserQuestion` call holding the four signal questions (phrased per [`../allocations/style.md`](../allocations/style.md)), each with exactly the four option labels from the matrix (one per class XS/S/M/L); an inferred answer is the first option marked `(Recommended)` with its evidence note as the description. Never one call per signal.
4. **Compute + confirm size and route — ONE question.** Apply the matrix rule: **size = highest signal**, with the single permitted talk-down for an effort-only outlier (named aloud). Derive the default route (**XS/S → `quick`, M → `standard`, L/XL → `full`**). Ask: «`<size>` — <the four answers in one line, e.g. `1 PR · ≤1 day · none · none`>. Route `<route>`: <the route's «In one line» cell from the cheat-sheet>. Lock both in?» — options:
   - `Yes — <size>, <route>` (Recommended)
   - `Yes, but route <alt>` — `<alt>` = the next-heavier route (`quick`→`standard`, `standard`→`full`, `full`→`standard`); any other route via «Other».
   - when the size is **L**: `XL — needs its own roadmap`; otherwise: `Different size` (asks which, free text via «Other» is fine).
   - `Adjust signals` — re-opens step 3 with the current answers pre-selected.
   Never a second question just for the route.

   **On a re-size, say what changes before asking** (only when step 1 found an existing `.size` and the user picked `Re-size`). List what already exists in `docs/features/<slug>/` and compare it against the MVP-vs-Full table in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md). Add one `Impact:` line per affected artifact to the question text, above the options:
   - **Crossing up (XS/S → M+)** — name every existing artifact the new size expects to be fuller, and the stage that fills it, e.g. «`spec.md` holds the test plan inline → M expects a separate `test-plan.md`: re-run `/foresdd:plan-tests <slug>`»; «`sad.md` has 2 ADRs, M typically has 5–12 → worth a second look in `/foresdd:design <slug>` (a range, not a quota)». List optional stages the old route skipped that the new route now runs or offers.
   - **Crossing down (M+ → XS/S)** — existing artifacts stay as they are. Nothing is deleted or trimmed, because filling a section later costs more than keeping one that is already written. Say so in one line, and name the stages that the lighter route will now skip or offer to skip from here on.
   - **Same band (XS↔S, M↔L/XL)** — the artifact set doesn't change, so write `Impact: none on existing artifacts` (plus the ADR range when it moves).
   - **Route-only change** (step 1 `Only the route`) — stages already done are not re-run. Only the remaining handoffs change, so name the next optional stage and what the new route does with it.
   - **Nothing written yet** (no artifacts besides `.size` / `.route`) → skip the `Impact:` lines.
   The impact lines are information, not extra questions. The confirm stays ONE question.
5. **Write `.size` + `.route`.** Each one line, plain text — `.size` only `XS`/`S`/`M`/`L`/`XL`; `.route` only `quick`/`standard`/`full` — no comments, no frontmatter. `docs/features/<slug>/.size`, `docs/features/<slug>/.route`.
6. **Re-sync the frontmatter mirrors (`.size` is the source of truth).** `feature_size:` lives in up to three places: the `.size` file (canonical) plus the `spec.md` and `sad.md` frontmatter (human-readable mirrors). For each of the two files that exists: same value → OK; different (a re-size, or a hand-edited mirror) → **update the frontmatter to the new `.size` value** and say so — never leave a mirror stale; missing field (the file has frontmatter but no `feature_size:`) → **add** `feature_size: <size>` and say so; a file without frontmatter is left alone and named in the handoff. If the user insists a mirror is the right value, that's a re-size — loop back to step 4 and re-confirm, then re-sync.
7. **Structural self-check** — per [`../allocations/self-check.md`](../allocations/self-check.md): re-read the written files from disk and verify **3 items**: (1) `.size` holds exactly one of {XS, S, M, L, XL} (one bare word, no trailing content); (2) `.route` holds exactly one of {quick, standard, full}; (3) every frontmatter mirror (`feature_size:` in `spec.md` / `sad.md`, for whichever has frontmatter) matches `.size`. Fix + re-check ≤2 cycles; surface anything unresolved.
8. **Commit + handoff.** Commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — after the self-check, `.size` + `.route` are **one** commit: `tshirt-size: <slug> .size+.route (<size>, route <route>)`; the re-synced `spec.md` / `sad.md` frontmatter mirrors (step 6), when changed, each get their own commit (`tshirt-size: <slug> spec.md feature_size`). Inline run by a wrapper (`specify` step 1) → don't commit here; the wrapper commits `.size`+`.route` at the end of its step. Then **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) (utility variant) — *What I did* (incl. the four signals, which were inferred vs answered, any talk-down, the `Impact:` lines on a re-size, and «self-check: 3/3 pass») + *Review* (`.size`, `.route`) + *Run next*: on a re-size whose impact named a stage to re-run, that stage first (e.g. `/foresdd:plan-tests <slug>`), with the backbone stage as the `↳ or`; on **XL**, `/foresdd:roadmap` (XL means it needs its own roadmap); otherwise resume your backbone stage (e.g. `/foresdd:specify <slug>`); `/clear` optional.

## Definition of Done

- `docs/features/<slug>/.size` holds exactly one of XS/S/M/L/XL; `docs/features/<slug>/.route` holds exactly one of quick/standard/full.
- The size follows the highest-signal rule (or a named effort-only talk-down); XL only via the explicit `XL — needs its own roadmap` choice.
- The user confirmed the classification — size AND route in one question (never silent, never two questions).
- On a re-size, the confirm question named the impact on the artifacts already written (or said there was none).
- If `spec.md` / `sad.md` exist, their `feature_size:` mirrors match `.size` (no drift; `.size` is the source of truth).

## Anti-patterns

- **Self-sizing without confirmation.** Inference pre-fills; the user locks it.
- **Optimistic «it's probably S».** Every signal is inferred *with evidence* or asked — never assumed.
- **Talking down a structural signal.** A migration or a breaking change sets the floor; only PR count / time may be talked down, by one class, aloud.
- **One `AskUserQuestion` per signal.** The four signals go in one call; the confirm is the second.
- **Overwriting an existing `.size` / `.route` without asking.**
- **A multi-line `.size` / `.route` with comments.** Wrappers grep them cheaply — keep each one bare word.
- **A second question just for the route.** Size + route confirm together; the route option rides in the same `AskUserQuestion`.
- **A silent re-size.** Changing M → S on a feature that already has a `test-plan.md` and five ADRs without saying what that means for them leaves the user guessing. Name the impact.
- **Deleting or trimming artifacts on a size-down.** The re-size changes `.size` / `.route` and the mirrors, nothing else.

## Example invocation

> **User:** «t-shirt size rate-limiting-per-user»
> **Skill:** `.size` absent → reads `spec.md`: infers `2–4 PRs` (three ACs, one service), `one of three` (new `/limits` endpoint), `internal only` (gateway is ours); time *unknown* → one call asks all four, three pre-marked `(Recommended)`, time without (`2–7 days` picked) → highest signal = **S** → default route **quick** → confirm: «S — 2–4 PRs · 2–7 days · one of three · internal only. Route quick: shortest legal path, optional stages that don't apply are skipped for you. Lock both in?» → `Yes` → writes `.size` = `S`, `.route` = `quick` → `spec.md` mirror updated → commits `tshirt-size: rate-limiting-per-user .size+.route (S, route quick)` and `tshirt-size: rate-limiting-per-user spec.md feature_size`.
>
> **Later — User:** «re-size rate-limiting-per-user, it now needs a public API»
> **Skill:** `.size` = `S` / route `quick` → `Re-size` → breaking changes now `public consumers` → **M**, route **standard** → confirm: «M — 2–4 PRs · 2–7 days · one of three · public consumers. Route standard: same stages, but every skippable stage is offered to you as a choice at its handoff. Impact: `spec.md` holds the test plan inline → M expects a separate `test-plan.md`: re-run `/foresdd:plan-tests rate-limiting-per-user`. Impact: `sad.md` has 1 ADR, M typically has 5–12 → worth a second look in design (a range, not a quota). Lock both in?» → `Yes` → writes, re-syncs both mirrors → Run next `/foresdd:plan-tests rate-limiting-per-user`.
