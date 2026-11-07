---
name: ux-flows
model: inherit
effort: high
agents: []
description: >
  Use to derive the user flows of a UI-touching feature after the spec is clarified — one mermaid
  flowchart per UI-touching §4 user story (happy + alt/error branches from §5 ACs), a screen
  inventory (SCR-NN ids), and an AC→flow map, written to docs/features/{slug}/ux-flows.md.
  Triggers on "ux flows for {slug}", "user flows for {slug}", "screen flow for {slug}",
  "/foresdd:ux-flows {slug}". Always markdown + mermaid regardless of the design tool; the Socratic
  pass confirms each flow in prose, never raw mermaid. Feeds design (target-surface evidence),
  sequences (SCR alignment), screens (the inventory) and plan-tests (e2e-through-UI paths).
  Hard-refuse if spec.md is missing; skipped for features with no human-facing UI.
---

# Skill: ux-flows

Draws **how the user moves** through a UI-touching feature — after `clarify`, before `design`. For
each UI-touching §4 user story it produces a mermaid `flowchart` (happy path + the alt/error
branches the §5 ACs demand), builds the **screen inventory** (`SCR-NN` — the id contract `screens`
details later), and maps every UI-touching AC to the flow/branch that shows it. The artifact is
**always markdown + mermaid** whatever `docs/design-system.md` picks as the drawing tool — flows
are flow-altitude, not visual design. `design` then reads it as **evidence** for the
target-surface + UI-architecture decisions (the formal `target_surfaces` declaration stays
`design`'s); `sequences` aligns UI-driven flows on the SCR ids; `plan-tests` takes the
e2e-through-UI paths from here.

**This stage is optional by surface, not by size:** its N/A condition (no human-facing UI) lives in
[`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) and is evaluated by `clarify`'s handoff
(`specify`'s when clarify was legally skipped). Invoked directly, it always runs.

Question phrasing → [`../allocations/style.md`](../allocations/style.md); each diagram is confirmed
**in prose, never as raw mermaid** → [`../allocations/diagram-presentation.md`](../allocations/diagram-presentation.md).

## Owner

PM + designer (or whoever owns the user experience). The PM confirms each flow matches a real user
story; the Tech Lead flags flows that imply architecture (they become `design` input, not decisions
here).

## Inputs

- `<slug>` — feature slug.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/spec.md` — the flows derive from §4 user
  stories + §5 ACs. Absent → STOP: «run `specify <slug>` first — ux-flows derives from its user
  stories».
- (Expected) `docs/design-system.md` — the platform posture (the default platform assumption) +
  the tool. **Absent → not a block**: work in `code`-mode assumptions, recommend
  `/foresdd:design-system` in the handoff.
- (Optional) `CONTEXT.md` (both levels, per-feature wins) — canonical roles for the actors.
- (Optional) `docs/features/<slug>/.size` / `.route` — depth + handoff resolution; absent → default
  M / standard and say so in the handoff.

## Protocol

1. **Gate + read.** `test -f docs/features/<slug>/spec.md` → missing = refuse with the pointer
   above. Read spec §1 (context), §4 (user stories — which touch a UI?), §5 (ACs), `CONTEXT.md`
   glossary, and `docs/design-system.md` (posture + tool; note its absence for the handoff).
2. **Set the depth dial + platform.** Resolve depth per the order in the interview-depth file:
   `--depth=` (this run) → `docs/features/<slug>/.depth` (reuse, one-line announce) → otherwise
   ONE depth-selection `AskUserQuestion` per [`../allocations/style.md`](../allocations/style.md)
   (`interview_depth` from `.claude/sdd.local.md`, else medium, as «(Recommended)»; answer
   written to `.depth`). Confirm the **platform posture** in the same call (its own question): the design-system posture as «(Recommended)», deviation
   allowed + recorded with its why. Depth governs the per-flow question volume
   (→ [`../allocations/interview-depth.md`](../allocations/interview-depth.md)); coverage never shrinks.
3. **Derive flows + inventory.** For every **UI-touching** §4 user story: one flow — happy path +
   an alt/error branch per relevant §5 AC. Collect every screen the flows visit into the
   **Screen inventory** (`SCR-NN` + purpose/entry/exit); flow nodes reference the SCR ids. A
   backend-only user story is listed as out of scope, not drawn.
4. **Socratic pass — prose, never raw mermaid.** Per
   [`../allocations/diagram-presentation.md`](../allocations/diagram-presentation.md): write each flow into
   `docs/features/<slug>/ux-flows.md` (bootstrapped from [`./templates/ux-flows.md`](./templates/ux-flows.md)
   on the first flow; each flow lands on disk as soon as it's drafted — progressive writes per
   [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md)),
   validate it parses per [`../allocations/mermaid-check.md`](../allocations/mermaid-check.md), then
   describe it with the shared template (header with `path:line`, numbered screens by `SCR-NN` +
   name, a `Branches:` bullet per decision/error edge) and confirm — at medium/hard via
   `AskUserQuestion`, up to 4 flows per call (Approve as is / Edit / Save as open question / Drop;
   a UI-touching story's flow is mandatory, so Drop re-asks once); at **easy**, write + one
   assumptions-ledger line per flow and proceed.
5. **Fill the AC map + write.** Complete the AC-coverage table (every UI-touching §5 AC →
   flow/node/branch, or an explicit `N/A: <reason>`) on disk, re-validate every mermaid block, stamp
   `updated_at`. No commit yet — it follows the self-check.
6. **Structural self-check** — per [`../allocations/self-check.md`](../allocations/self-check.md): re-read
   the file from disk and verify **4 items**: (1) every UI-touching §4 user story has a flow;
   (2) every flow node's SCR id exists in the inventory (and every inventory row appears in ≥1
   flow); (3) every UI-touching §5 AC appears in the coverage table with a flow/branch or an
   explicit N/A; (4) every mermaid block parses. Fix + re-check ≤2 cycles; surface anything
   unresolved.
7. **Commit + handoff.** On a passing self-check, **commit per
   [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md)** — one commit for
   `ux-flows.md` (`ux-flows: <slug> ux-flows.md`); an unresolved item means no commit. Then emit the
   **stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md)
   — *What I did* (incl. «self-check: 4/4 pass» + the commit SHA; + «`docs/design-system.md` absent — run
   `/foresdd:design-system`» when it was) + *Review* (`docs/features/<slug>/ux-flows.md`) + *Run next*:
   `/clear`, then `/foresdd:design <slug>` (it reads these flows as target-surface evidence).

## Definition of Done

- `docs/features/<slug>/ux-flows.md` exists: platform decisions, the SCR-NN inventory, one flow per
  UI-touching §4 user story (happy + AC-demanded branches), the AC-coverage table — zero silently
  uncovered UI ACs.
- Every flow was confirmed in prose (or written + ledgered at easy); every mermaid block parses.
- No visual design leaked in: no component names, no layout, no styling — flow altitude only
  (screens is where states + components live).

## Anti-patterns

- **Drawing screens here.** Components, states, layout belong to `screens`; this artifact is the
  movement between screens, not their content.
- **Deciding architecture here.** «SPA vs SSR», «this needs a websocket» — flag it as design input;
  `design` decides and declares `target_surfaces`.
- **Raw mermaid as the confirmation prompt** — the anti-pattern
  [`diagram-presentation.md`](../allocations/diagram-presentation.md) exists to kill.
- **Skipping backend-only stories silently.** List them as out of scope with one line — the reader
  must see they were considered.
- **Blocking on a missing design-system.** Its absence degrades (code-mode assumptions + a handoff
  recommendation), never blocks the flow work.

## References & template

- [`./templates/ux-flows.md`](./templates/ux-flows.md) — output scaffold; inline comments are the
  generation contract.
- [`../allocations/diagram-presentation.md`](../allocations/diagram-presentation.md) ·
  [`../allocations/mermaid-check.md`](../allocations/mermaid-check.md) — confirm-in-prose + parse-validation.
- [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) — the N/A condition (no human-facing UI)
  evaluated by the upstream handoff.
- [`../allocations/interview-depth.md`](../allocations/interview-depth.md) — the depth dial set in step 2.
