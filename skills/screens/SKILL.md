---
name: screens
model: inherit
effort: high
agents: []
description: >
  Use to produce the canonical screen manifest for a UI feature — every screen in every state
  (default / loading / empty / error / success / validation), with reuse-first component picks —
  written to docs/features/{slug}/screens.md between api and tasks. Draws per the design-system
  tool: Figma MCP into the canon file, Pencil MCP into screens.pen, or inline markdown wireframes
  (code mode — also the degradation when an MCP is unavailable). Triggers on "screens for {slug}",
  "screen states for {slug}", "draw the screens", "mockups for {slug}", "/foresdd:screens {slug}".
  States derive from §5 ACs + sad.md §6 branches + contract error responses;
  tasks/implement/review read ONLY the manifest. Hard-refuse if sad.md is missing; skipped when
  target_surfaces declares no UI surface.
---

# Skill: screens

Turns the approved architecture into the **screen manifest** — the one artifact `tasks`,
`implement` and `review` read for what every screen shows in every state. It runs **between `api`
and `tasks`**: by then the states are *derivable*, not invented — `default` plus every state the
spec §5 ACs, the `sad.md` §6 `alt`/`else` branches, and the contract error responses imply
(loading / empty / error / success / validation). Per state it names the **components to reuse**
from the `docs/design-system.md` inventory — a `NEW:` component only with a
why-no-primitive-fits justification. The visuals are drawn per the canon's `tool`; whatever the
tool, **the manifest is the contract** — downstream never reads the raw Figma/`.pen` file.

**Optional by surface:** its N/A condition (no UI surface in `sad.md` `target_surfaces`) lives in
[`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) and is evaluated by `api`'s handoff
(carried forward when `api` itself is N/A). Invoked directly, it always runs.

Question phrasing → [`../allocations/style.md`](../allocations/style.md).

## Owner

Designer + frontend lead. The PM confirms the states match the ACs; `review` later checks the
built screens against this manifest.

## Inputs

- `<slug>` — feature slug.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/sad.md` — `target_surfaces` + the §6
  branches feed the state derivation. Absent → STOP: «run `design <slug>` first».
- (Expected) `docs/features/<slug>/ux-flows.md` — the SCR inventory this manifest details.
  **Absent → soft**: offer `/foresdd:ux-flows <slug>` first, or derive the inventory from spec §4 +
  the SAD with a **noted gap** in the manifest — never a silent invention.
- (Expected) `docs/design-system.md` — the `tool` + the component inventory. Absent → `code` mode
  + recommend `/foresdd:design-system` in the handoff.
- (Read) `docs/features/<slug>/contracts/` (error responses → error states), `spec.md` §5 (ACs →
  states), `.size`/`.route` (depth + handoff resolution; defaults stated loudly when missing).

## Protocol

1. **Gate + read.** `test -f docs/features/<slug>/sad.md` → missing = refuse with the pointer
   above. Read `target_surfaces` (no UI surface declared → say so and STOP — this stage is for UI
   features; the upstream handoff normally skips it). Read `ux-flows.md` (or run the soft fallback
   above), `docs/design-system.md` (`tool` + inventory), `sad.md` §6, `contracts/`, spec §5.
   Resolve the depth as a **reading stage** per
   [`../allocations/interview-depth.md`](../allocations/interview-depth.md) (`--depth=` → `.depth` →
   `interview_depth` → medium): never ask for it, announce the level in one line, and don't write
   `.depth` when it was absent. Depth governs the confirm volume in step 5.
2. **Fix the drawing mode — once, before any screen.** The mode is the canon's `tool`, checked
   against this session:
   - **Its MCP is unavailable** → mode `code`, a **named degradation** per
     [`../allocations/fallbacks.md`](../allocations/fallbacks.md): frontmatter `tool: code` +
     `degraded_from: <canon tool>`, one line in §Source, one line in the handoff. Never block.
   - **`pencil`** → the **active-document gate** before the first write, the same as
     `design-system` step 5b: absent `docs/features/<slug>/screens.pen` → write the minimal stub
     (`{"version": "2.17", "children": []}`); ask the user to open it in the Pencil app; verify via
     `get_app_state` that the active document IS that `screens.pen`. Mismatch — the canon's
     library `pen_file` or any other document is active → stop and repeat the ask; **never draw
     into a document that isn't this feature's `screens.pen`**. Re-run the check before each
     batch's writes (the user may switch documents mid-run).
   - **`figma`** → draw into the canon's `figma_file`.

   Bootstrap [`./templates/screens.md`](./templates/screens.md) → `docs/features/<slug>/screens.md`
   with frontmatter `tool` = **the mode actually used** (not blindly the canon's) and §Source.
3. **Derive states per screen.** For each `SCR-NN` from the inventory, list the **full state set**:
   `default` + every state the ACs / §6 branches / contract errors imply; a state class that
   genuinely doesn't apply gets one explicit `N/A: <reason>` row. Pick the components per state —
   **from the design-system inventory by name**; a `NEW: <name>` only when no existing primitive
   fits, with the one-line why.
4. **Draw + write, in batches of ≤4 screens.** For each screen in the batch, draw per the mode —
   `figma` → the Figma MCP, record the node-id per state; `pencil` → the Pencil MCP, record the
   node id per state; `code` → inline wireframes. **Code wireframes stay compact** so they fit a
   question preview: ≤ 40 characters wide, ≤ 16 lines, plain ASCII box-drawing (`+ - |`), one
   block per state with a **distinct layout** — a state that only swaps a component (e.g. `Button`
   → loading) is a table row, not a new wireframe. Write each `### SCR-NN` section (and any §New
   components rows it adds) to disk **as soon as it is drawn** — progressive writes per
   [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — so the user can open
   the file while the confirm is on screen.
5. **Confirm the batch.** **medium / hard** → ONE `AskUserQuestion` per batch, one question per
   screen (≤4), phrased per [`../allocations/style.md`](../allocations/style.md). Each question
   names the screen (`SCR-NN — <name>`, `path:line` of its section), lists its states with the
   AC / §6 branch / contract error each traces to, and any `NEW:` component with its why. Options
   are the canonical four — **Approve as is** / **Edit** / **Save as open question** / **Drop** (an
   inventory screen is mandatory, so Drop re-asks once; a screen that truly shouldn't exist is a
   `ux-flows` fix, said so in the handoff). **Every option carries the same `preview`** so the
   screen stays visible whichever option is focused: in `code` mode the `default` wireframe plus
   one line per state (`error — AC-2: inline under Input`); in `figma`/`pencil` the state table
   with node-ids (the canvas is the visual). **Edit** → apply, rewrite the section, re-confirm that
   screen in the next batch. **easy** → no confirm; one assumptions-ledger line per screen, and a
   question (same shape + preview) only where the AC ↔ state mapping is genuinely ambiguous.
   Stamp `updated_at` after the last batch. No commit yet — it follows the self-check.
6. **Structural self-check** — per [`../allocations/self-check.md`](../allocations/self-check.md): re-read
   the manifest from disk and verify **4 items**: (1) every `SCR-NN` from `ux-flows.md` has a
   section (inventory fully covered — or the noted-gap fallback is stated); (2) every screen shows
   ≥ `default` + (`error` or `empty`) — or carries the explicit `N/A: <reason>` row; (3) every
   component name exists in the design-system inventory or sits in §New components with a
   justification; (4) keyed to the frontmatter `tool` (the mode used): `figma`/`pencil` → every
   state row carries a source-ref (node-id); `code` → the wireframes are present, and a
   `degraded_from` is named in §Source. Fix + re-check ≤2 cycles; surface anything unresolved.
7. **Commit + handoff.** On a passing self-check, **commit per
   [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md)** — one commit for
   `screens.md` (`screens: <slug> screens.md`) and, on `pencil`, first ask the user to **Cmd+S in
   Pencil** (the app holds changes in memory; the MCP cannot save), then one commit for
   `screens.pen` (`screens: <slug> screens.pen`) only when `git status` shows it changed — an
   unsaved `.pen` is named in the handoff, not committed. Figma lives outside the repo, nothing to
   commit. An unresolved item means no commits. Then emit the
   **stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md)
   — *What I did* (tool used or the degradation, «self-check: 4/4 pass», the commit SHAs) + *Review*
   (`docs/features/<slug>/screens.md`, + `screens.pen` / the Figma file when tool-drawn) + *Run
   next*: `/clear`, then `/foresdd:tasks <slug>` (each `ui` task will cite these SCR ids + states).

## Definition of Done

- `docs/features/<slug>/screens.md` exists: §Source per the canon's tool, one section per SCR with
  the derived state table, components reuse-first (`NEW:` only justified), §New components filled
  or explicitly «None».
- States are **derived** — every error/empty state traces to an AC, a §6 branch, or a contract
  error response; nothing invented, nothing silently missing.
- For `figma`/`pencil`: every state has its node source-ref; for `code`: the wireframes are inline.
- The manifest is the only thing downstream needs — `tasks`/`implement`/`review` never open the
  raw design file.

## Anti-patterns

- **Happy-path-only screens.** A screen with just `default` hides exactly the states users hit —
  the error/empty derivation is the point of this stage.
- **Inventing states with no source.** Every non-default state traces to an AC / branch / contract
  error; a state with no origin is scope creep in a costume.
- **Hand-rolling a component the inventory already has** — the reuse rule this pipeline exists to
  enforce; `NEW:` requires the why-no-primitive-fits line.
- **Blocking on a missing MCP.** `code` mode is always available — degrade with a named
  degradation, never refuse the stage over tooling.
- **Recording the canon's tool after degrading.** A manifest that says `tool: pencil` but holds
  ASCII wireframes fails its own self-check and misleads `review` — record the mode actually used
  (`tool: code`, `degraded_from: pencil`).
- **Drawing into whatever `.pen` is open.** The Pencil MCP writes into the app's active document
  and ignores `filePath` — skipping the `get_app_state` check draws this feature's screens into
  the canon library or someone else's file.
- **Confirming a screen the user can't see.** A state table alone is abstract — in `code` mode
  the wireframe rides in the question's `preview`, written to disk before the question is asked.
- **Making downstream read the design file.** Node-ids are source-refs for humans; the manifest
  carries everything `tasks`/`implement`/`review` consume.
- **Architecture decisions here.** The surface set, SSR-vs-SPA, state management — all `design`'s;
  screens details what was declared, it never re-decides.

## References & template

- [`./templates/screens.md`](./templates/screens.md) — the manifest scaffold; inline comments are
  the generation contract.
- [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) — the N/A condition (no UI surface)
  evaluated by `api`'s handoff.
- [`../allocations/fallbacks.md`](../allocations/fallbacks.md) — the design-tool MCP degradation
  rule (fall back to code mode, named).
- [`../allocations/surfaces.md`](../allocations/surfaces.md) — the surface declaration this stage gates on.
