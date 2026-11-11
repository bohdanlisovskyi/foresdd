---
name: design
model: inherit
effort: high
agents: [explorer, critic]
description: >
  Use to produce a Software Architecture Document for a feature — Arc42 12 sections + C4 L1/L2
  inline + ADRs spawned on a blast-radius gate — once spec.md exists. Triggers on "design {slug}",
  "architecture for {slug}", "SAD for {slug}", "arc42 for {slug}", "C4 context+container for
  {slug}", "/foresdd:design {slug}". Drafts §1–§12, batch-validates each section Socratically (4-state
  machine), spawns an ADR only when a decision crosses the blast-radius threshold (irreversible /
  multi-module / has legitimate alternatives), writes each resolved section + its ADRs to disk
  immediately, then runs a clean-context critic and commits sad.md + each ADR separately.
  Resumes a partly written sad.md from the first unresolved section. Brownfield: reads
  docs/architecture-map.md, or dispatches an Explore subagent when the map is absent or stale.
  Hard-refuse if spec.md is missing; CONTEXT.md is optional (when present its Glossary is canonical).
---

# Skill: design

Generator of the **Software Architecture Document** (`docs/features/<slug>/sad.md` — Arc42 12 sections, C4 Context inline in §3 and C4 Container inline in §5) plus supporting ADRs (`docs/features/<slug>/adr/NNNN-*.md`). It drafts all 12 sections in memory, walks them Socratically one section at a time, spawns an ADR only when a decision's *blast radius* (how painful it is to reverse the decision later) crosses the gate, writes each resolved section and its ADRs to disk as soon as it resolves, runs a clean-context critic over the finished SAD, and then commits once per document — `sad.md` plus each ADR on its own — per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md). The document itself is the state — resuming after an interrupt is free. L3 Component / L4 Code are out of scope. This file is the spine; detail lives in `references/`.

The Socratic machine, the critic, and the T-shirt sizing matrix are **shared** — this skill keeps only its deltas:
→ [`../allocations/socratic-loop.md`](../allocations/socratic-loop.md) · [`../allocations/critic.md`](../allocations/critic.md) · [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) · [`../allocations/style.md`](../allocations/style.md)

Depth governs the per-section question volume + autonomy → [`../allocations/interview-depth.md`](../allocations/interview-depth.md). C4 diagrams are confirmed in prose, never as raw source → [`../allocations/diagram-presentation.md`](../allocations/diagram-presentation.md). design is also where the feature's **target surface(s)** are chosen — the first §4 decision, written to `sad.md` frontmatter `target_surfaces` and read (never re-derived) by every downstream stage → [`../allocations/surfaces.md`](../allocations/surfaces.md).

## Owner

Architect / Tech Lead (drives everything). PM is consulted only on §10 Quality goals and §11 Risk severities.

## Inputs

- `<slug>` — same feature slug used by every earlier stage.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/spec.md`. If absent → STOP and point: «run `specify <slug>` first — design reads the spec's goals/NFRs as canonical».
- (Optional) `CONTEXT.md` — repo-root and/or `docs/features/<slug>/` → [`../glossary/SKILL.md`](../glossary/SKILL.md). When present, its `## Glossary` is canonical for roles + domain terms (per-feature wins over root on conflict); when absent, the spec's §4 roles are canonical and the handoff recommends `/foresdd:glossary <slug>` before terms drift.
- (Optional) `docs/features/<slug>/ux-flows.md` — the user flows + SCR screen inventory from `ux-flows`. When present it is **evidence** for the §4 Target-surface + UI-architecture decisions and for the §5 containers — read it in step 2; its absence on a UI-touching feature is legal (the stage may have been skipped) but worth naming in the handoff.
- (Optional) `docs/features/<slug>/.size` — depth hint (MVP vs Full + expected ADR count per the T-shirt sizing matrix). Absent → default to M (full set) **and say so loudly in the handoff** — «size M (default — no `.size`; run `/foresdd:tshirt-size <slug>`)».
- A git repo — so the Step-3 Explore subagent can read code on a brownfield.
- **Existing `sad.md`** → resume, never overwrite (step 4). All 12 sections already resolved → nothing to walk: say so and suggest `/foresdd:sequences <slug>` (or the critic re-run via step 7 if it never committed).

## Protocol

1. **Gate + size + set interview depth.**
   - **Gate.** `test -f docs/features/<slug>/spec.md` → missing = refuse with the pointer above. Frontmatter `kind: baseline` → refuse too: «`<slug>` is a baseline (what the code does today), not a change — design the change under its own slug: `/foresdd:specify <change-slug>` (it sets `extends: <slug>`)».
   - **Size + route.** Read `.size` if present (shapes ADR count + §6 flow count — see the T-shirt sizing matrix) and `.route` if present.
   - **Depth**, per the resolution order in [`../allocations/interview-depth.md`](../allocations/interview-depth.md): `--depth=` (this run) → `docs/features/<slug>/.depth` (reuse, one-line announce — the normal case after `specify`) → otherwise ONE depth-selection `AskUserQuestion` phrased per [`../allocations/style.md`](../allocations/style.md), with `interview_depth` from `.claude/sdd.local.md` (else medium) as the «(Recommended)» first option — **except on route `quick`, where `easy` is the «(Recommended)» first option** (the quick-route softening per the Routes table in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md)). Write the answer to `.depth`.
   - **What depth changes** — the step-6 per-section question volume and the C4 confirmation:

     | Depth | Step-6 behaviour |
     |---|---|
     | easy | Decide convention-defaults yourself + log them in the assumptions ledger; ask only blast-radius decisions; C4 diagrams written + one ledger line, no question. |
     | medium | Walk every real decision. |
     | hard | Walk every decision and foreground each trade-off. |

     **Floors at every depth:** the blast-radius → ADR gate and the §11 owner+due rule.
2. **Read upstream.** `spec.md` (§2 Goals, §3 Non-goals, §6 NFR with numeric targets + measurement, §6.1 Security/privacy + abuse cases, §7 KPIs, §8 Open questions, any §1 ¶4 «Decision override» bullets); when the spec's frontmatter has `extends: <area>`, also `docs/features/<area>/spec.md` §4/§5/§9 — the baseline behaviour the SAD must keep unless an AC says it `supersedes` it; `docs/features/<slug>/ux-flows.md` when present (platform decisions, flows, the SCR inventory — evidence for the §4 Target-surface + UI-architecture decisions and the §5 containers); `CONTEXT.md` `## Glossary` when present — read **both** repo-root (project-wide) and `docs/features/<slug>/CONTEXT.md` (feature-scoped); per-feature wins on conflict; canonical roles + domain terms win over anything that contradicts. Neither file exists → the spec's §4 roles are canonical; recommend `/foresdd:glossary <slug>` in the handoff.
3. **Current architecture — read the map, don't re-scan.** Prefer `docs/architecture-map.md` (produced by `survey`): if it exists and is fresh (its `reflects_commit` ≈ current HEAD), read it — that IS the brownfield context (module layout, layering, datastores, conventions, the C4 of what exists). Re-scan only if the map is **absent or stale**: dispatch the [`explorer`](../../agents/explorer.md) agent — `subagent_type: "foresdd:explorer"` (`model: haiku` + `effort: low`, clean-isolated per [`../allocations/agent-roster.md`](../allocations/agent-roster.md)) — for «module layout, layering/ports conventions, datastores, inter-module comms, anything that constrains `<slug>`», and suggest the user run `survey` to persist it. Greenfield (no source + no map) → note `<!-- brownfield: N/A — greenfield repo -->` in §3. (Fallback to a `subagent_type: "Explore"` Agent if `explorer` unavailable.)
4. **Bootstrap — or resume.**
   - **No `sad.md`** → copy [`./templates/sad.md`](./templates/sad.md) → `docs/features/<slug>/sad.md`; patch frontmatter (`updated_at`, `feature_size` from `.size`; leave `target_surfaces: []` empty — filled when §4's Target-surface decision resolves in step 6).
   - **`sad.md` already exists → resume, never re-copy the template.** A section counts as **resolved** when it holds real content or a `<!-- N/A: … -->` note and no `<placeholder>` stub. Rebuild state from disk: resolved sections are kept as-is (never re-walked); §9 rows + `adr/` files seed the ADR-spawns log; §11 `Open question` rows seed the edits-log's `save_as_oq` entries; a non-empty `target_surfaces` means the §4 Surface decision is done. Announce in one line — «Resuming design for `<slug>`: §1–§5 already on disk (3 ADRs), continuing at §6» — then draft (step 5) and walk (step 6) **only the unresolved sections**. All 12 resolved → skip to step 7 if nothing was committed yet, else stop per the Inputs note.
   - No commit here — commits happen once, at the end of step 7. Read the template's `<!-- … -->` comments (the per-section contract) + [`./templates/adr.md`](./templates/adr.md) (MADR shape). This is the only file write between step 4 and step 6 — step 5 drafts in-memory.
5. **Per-section draft (in-memory).** For each unresolved section in §1 → §12, draft proposed content + the decisions it contains, bundling trivial convention defaults into one question. Per-section sourcing, item-banks, the question budget, and pre-Socratic hygiene → [`./references/draft-generation.md`](./references/draft-generation.md). Do NOT write `sad.md` here.
6. **Socratic walk + blast-radius gate, per-section write.** For each unresolved section §1 → §12:
   - **a. Render** the full section + its numbered decisions (big picture). Open every question's text with a progress tag — `[§4 Solution strategy · 4/12]` — so the user always knows where they are in the pass.
   - **b. Walk** the decisions with the shared 4-state machine — batched ≤4 per `AskUserQuestion`, with the «Approve whole section» fast path when no decision is gate-worthy (per the shared loop). Question volume follows the depth table in step 1. Apply transitions in-memory. design delta → [`./references/socratic.md`](./references/socratic.md) (section list, decision-types, the gate); design-specific question shapes → [`./references/ask-examples.md`](./references/ask-examples.md).
   - **c. Gate** each **Approved** decision with the blast-radius gate → spawn an ADR on 2-of-3 ([`./references/blast-radius.md`](./references/blast-radius.md)).
   - **d. Write** the resolved section + its spawned ADRs to disk immediately — **no commit here**, on any route or depth (an interrupt loses nothing: the disk already holds every resolved section, and step 4 resumes from it). Never return to a written section. Maintain the edits-log + an adjacent ADR-spawns log.
   - **§4 special case — Target surface first.** §4's first decision is *what's being built* (`backend-service` / `web-frontend` / `mobile-app` / `desktop-app` / `cli` / `worker` / `library-sdk`), derived from spec §1 «for whom» + §4 roles, **with `ux-flows.md` as evidence when it exists** (a real screen inventory is a strong signal for a UI surface; the spec itself names no surface). Multi-surface is multi-module + irreversible ⇒ usually an ADR. On resolution, **write `target_surfaces: [...]` to the `sad.md` frontmatter** — it draws one §5 C4 container per surface and is read (never re-derived) by `api` / `sequences` / `tasks` / `plan-tests` / `review`. For each declared **UI surface**, walk the follow-on **UI-architecture decision** (web → SSR/SPA/hybrid; mobile → native/cross-platform; + state/routing if warranted), gated to an ADR like any §4 strategic choice → [`../allocations/surfaces.md`](../allocations/surfaces.md).
   - **§3 / §5 special case — C4 diagrams**, per [`../allocations/diagram-presentation.md`](../allocations/diagram-presentation.md): write the block into `sad.md`, validate it, then **describe it with the shared template** (header with the fence's `path:line`; §3 as Who uses it / What it depends on / What it writes to, §5 as one line per container) and confirm by that description — **never paste the raw C4 source as the question**. Both views are mandatory — Drop re-asks once. At `easy`, write + one assumptions-ledger line and proceed. Syntax → [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md).
7. **Critic + finalize.**
   - **a. Critic.** Dispatch the [`critic`](../../agents/critic.md) agent — `subagent_type: "foresdd:critic"` (clean-isolated per [`../allocations/agent-roster.md`](../allocations/agent-roster.md); **model per `judgment_model`; effort `xhigh` on L/XL** via `CLAUDE_CODE_EFFORT_LEVEL`; fallback `general-purpose` if unavailable) — with the design delta in [`./references/critic.md`](./references/critic.md) (over [`../allocations/critic.md`](../allocations/critic.md)) on the final `sad.md` + edits-log + ADR-spawns log.
   - **b. Resolve findings** per the shared resolution flow: summary table → batched `AskUserQuestion` with before/after previews, options per fix-type; Override-with-rationale → §1 ¶4 bullet; at `easy` mechanical fixes auto-apply; one bounded re-check.
   - **c. Backstop scans** (this skill's structural self-check): **every Mermaid block in `sad.md` validated per [`../allocations/mermaid-check.md`](../allocations/mermaid-check.md)** (the structural lint script, plus a full `mmdc` parse when installed — fix any that don't parse, never commit a broken diagram); ADR titles in decision-form kebab-case + Status `Accepted`; §9 closed against `adr/`; no `<placeholder>` stubs.
   - **d. Commit** — on pass, write any amendments, then commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md): one commit per ADR (`design: <slug> ADR-NNNN <title>`) and one for `sad.md` (`design: <slug> sad.md`). An unresolved self-check item means no commits.
   - **e. Handoff** — emit the stage-handoff block per [`../allocations/handover.md`](../allocations/handover.md): *What I did* + *Review* (`sad.md`, `adr/`) + *Run next*, resolved per `.route` (the Routes table in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md)):
     - forward → `/foresdd:sequences <slug>` (writes flows into §6);
     - `sequences`' N/A condition = **one actor and no multi-step runtime flow** → skip target `/foresdd:data-model <slug>` (on `quick` — auto-skip with the reason + inverted `↳ or`; on `standard` — offer the `↳ or`; on `full` — no skip line);
     - when skipping, carry the next N/A conditions forward in order: no schema change either → `/foresdd:api <slug>`; no contract change either → `screens`' N/A condition (no UI surface in `target_surfaces`) → `/foresdd:screens <slug>`, or `/foresdd:tasks <slug>` when that holds too.

## Definition of Done

- `docs/features/<slug>/sad.md` exists with all 12 Arc42 sections filled OR marked `<!-- N/A: <reason> -->`.
- §3 has a real `C4Context` block and §5 a real `C4Container` block — real names from the glossary/spec + the scan, no `<placeholder>` stubs, no `Container_Bondary` typos. §6 has ≥1 `sequenceDiagram` (the `sequences` stage then covers every critical flow / §5 AC — no cap).
- Frontmatter `target_surfaces: [...]` is non-empty (the Target-surface decision was made in §4) and §5 draws **one C4 container per declared surface**; each declared UI surface (`web-frontend` / `mobile-app` / `desktop-app`) carries a UI-architecture decision — an ADR, or an inline §4 note if it didn't cross the gate. → [`../allocations/surfaces.md`](../allocations/surfaces.md).
- §9 ADR table is closed against `adr/` (every file has a row, every row a file). ADR count within the typical range per [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) (XS 0–2, S 1–4, M 5–12, L/XL 10–15 — a range, not a quota; the blast-radius gate decides); every ADR Status = `Accepted`, title in decision-form (`0003-sliding-window-counter.md` ✓ vs `0003-rate-limiting.md` ✗), no strawman options.
- §10 scenarios are testable (When / Then / How-verify) and cite spec §6 NFR numbers verbatim (no inventing, no rounding).
- §11 carries a row for every `save_as_oq` decision with both owner AND due (severity literal `Open question`); never N/A.
- §1 Stakeholders + §3 actors match the glossary exactly when a `CONTEXT.md` exists (per-feature wins over root), else the spec's §4 roles (no invented `user`/`admin`).
- Step-3 Explore ran on a brownfield (or §3 has the greenfield note). Edits-log maintained. The critic ran on the post-Socratic SAD; every finding resolved or overridden.
- The step-7 critic + pre-write backstop scans (mermaid-check, ADR-title form, §9 closure, no-placeholder) are this skill's **structural self-check** ([`../allocations/self-check.md`](../allocations/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **An ADR for every decision** — kills the genre. Only blast-radius decisions become ADRs (5–12 for M, not 25). Conversely, missing an irreversibility under-ADRs the feature.
- **ADR `Status: Proposed` from this skill** — it is synchronous (you decide with the user now), so Status is `Accepted`. Use `decide-adr` for an async Proposed → Accepted flow.
- **ADR title in problem-form** (`0003-rate-limiting.md`) or with a **strawman option** (an alternative an existing constraint already excludes) — both dilute the ADR genre and trigger the critic's F6.
- **Inventing §10 numbers** the spec never agreed to — cite spec §6 NFR verbatim. **Naming a concrete stack in §2** that contradicts the repo's conventions without an Override note pointing at §11.
- **Skipping the Step-3 Explore on a brownfield** — guessing the layout produces a fictional §5 Container view and invented §2 Constraints.
- **Re-copying the template over an existing `sad.md`** — wipes every resolved section. Resume from disk (step 4).
- **Returning to a written section** — each section lands on disk as it resolves; cross-section drift is the critic's job, not a re-walk. Re-opening §4 after writing §10 means you don't trust the per-section batch.
- **Save-as-OQ without owner+due** — capture both in the follow-up; missing either downgrades to Drop with a warning, never a half-filled §11 row.
- **Resolving critic findings unilaterally** (without `AskUserQuestion`) — defeats the user-in-the-loop contract. **Per-section or batched commits** — the disk already protects an interrupted pass; history gets one `sad.md` commit + one per ADR, after the self-check.
- **Spilling into C4 L3/L4** — out of scope; suggest a separate diagramming pass.

## References & template

- [`./references/draft-generation.md`](./references/draft-generation.md) — Step 5: per-section sourcing for §1–§12, item-banks, the question budget, pre-Socratic hygiene.
- [`./references/socratic.md`](./references/socratic.md) — design's delta over the shared Socratic loop (section list, decision-types, the blast-radius gate, the §11 OQ table).
- [`./references/blast-radius.md`](./references/blast-radius.md) — the 3-criteria ADR gate (irreversible / multi-module / legitimate alternatives), scoring, target counts.
- [`./references/critic.md`](./references/critic.md) — design's delta over the shared critic (F5 floor, F6 = NFR-leak + strawman-ADR + §2-vs-repo, F1 = strategic-vector drift).
- [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md) — C4Context + C4Container Mermaid cheatsheet for §3/§5.
- [`./references/ask-examples.md`](./references/ask-examples.md) — design-specific question shapes (strategic-with-ADR-spawn, blast-radius gate, Save-as-OQ follow-up).
- [`../allocations/interview-depth.md`](../allocations/interview-depth.md) — the easy/medium/hard dial set in step 1 (per-section question volume + autonomy).
- [`../allocations/diagram-presentation.md`](../allocations/diagram-presentation.md) — how the §3/§5 C4 diagrams are confirmed in prose (write → validate → describe), never as raw source.
- [`../allocations/surfaces.md`](../allocations/surfaces.md) — the target-surface taxonomy (C4-container-grounded); design owns the selection (§4 first decision → frontmatter `target_surfaces`), downstream reads it.
- [`./templates/sad.md`](./templates/sad.md) · [`./templates/adr.md`](./templates/adr.md) · [`./templates/deployment.md`](./templates/deployment.md) — output scaffolds; inline comments are the per-section generation contract. (C4 syntax → [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md).)
