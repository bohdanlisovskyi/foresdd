---
name: survey
model: inherit
effort: medium
agents: [explorer]
description: >
  Use to establish the repo's architecture map the rest of the pipeline reads. Two modes: on an
  EXISTING codebase it scans once and persists what's there; on an EMPTY/greenfield repo it runs a
  short, level-adaptive foundation session — picks the stack / folder structure / data approach /
  conventions WITH you (defaults-heavy), fixes them as the foundation + foundational ADRs, and
  emits a scaffold tasks.json that the scaffold skill materializes into a real skeleton. Triggers
  on "survey the codebase", "map the architecture", "set up a new project", "bootstrap the
  foundation", "/foresdd:survey". Output: docs/architecture-map.md (+ adr/ + scaffold tasks.json on
  greenfield). Records reflects_commit for staleness; reads, never overwrites, an authored
  architecture doc.
---

# Skill: survey

The pipeline's anchor on architecture. It produces `docs/architecture-map.md` — the single source of "what the system is" that `specify` (constraints), `design` (matches against it), `data-model`, and `implement` all read instead of re-discovering the code. It runs in one of **two modes**, auto-detected:

- **Brownfield** (the repo has source) → scan it once and persist the **current** architecture.
- **Greenfield** (empty / near-empty repo) → run a short, **level-adaptive foundation session**: pick the stack / structure / data approach / conventions *with* the user (defaults-heavy), fix them as the **foundation** + foundational ADRs, and emit a **scaffold `tasks.json`** that [`scaffold`](../scaffold/SKILL.md) turns into a real skeleton. Greenfield detail → [`./references/foundation.md`](./references/foundation.md).

Repo-level utility (one map serves every feature). The scan is delegated to [`explorer`](../../agents/explorer.md); question phrasing → [`../allocations/style.md`](../allocations/style.md); depth → [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md).

## Owner

Architect / Tech Lead — they own the architecture (brownfield: confirm it reflects reality; greenfield: decide the foundation).

## Inputs

- (Optional) a path/scope hint (default: repo root).
- (Read, never overwrite) an authored architecture doc if present (`docs/architecture.md`, `ARCHITECTURE.md`, root `CLAUDE.md`, ADRs) — a strong input the map reconciles with, never clobbers.
- (Optional, greenfield) `docs/idea-brief.md` — the intent G3 would otherwise ask for; present → confirmed, not re-asked.

## Protocol

1. **Ensure the settings file, then detect the mode.**
   - **Ensure the settings file (first thing, after this skill's own gate).** If `.claude/sdd.local.md` is absent, create it now from the canonical template — documented defaults + the self-documenting body — and patch `.gitignore`; if it exists, read it and never overwrite. The one procedure lives in [`../allocations/settings-file.md`](../allocations/settings-file.md). Creating is unconditional; **changing values is only ever offered by [`config`](../config/SKILL.md)**. Say the one-line creation notice from the canon (only when the file was just created).
   - **Map exists and is fresh** (its `reflects_commit` ≈ current HEAD) → «map is fresh (reflects `<commit>`). Reuse or refresh?»; STOP on reuse.
   - **Map exists but is stale** → prefer the **incremental re-survey**: `git diff --name-only <reflects_commit>..HEAD`, group the changed paths by top-level module, and dispatch the step-3 explorer **scoped only to the changed subfolders**; update just the touched map rows/sections (module inventory, conventions, frontend, machine keys) and re-stamp `updated_at` + `reflects_commit`. Fall back to the **full re-scan only when the diff spans more than half the modules** in the inventory (or `reflects_commit` no longer resolves) — say which mode ran in the handoff.
   - **No map** → **brownfield** if the repo has source (modules/packages beyond config), else **greenfield** (empty or only scaffolding like a bare `go.mod` / `package.json`). Borderline (a handful of source files — a spike, a tutorial leftover) → ask once: «map what's here, or treat this as a fresh start and choose the foundation together?»
   - **Tell the user what's about to happen**, in one or two lines, before any scan or question: the mode, what will be written, and roughly what comes after — brownfield: «Scanning the repo to write `docs/architecture-map.md`; I'll show you a summary to confirm before committing.»; greenfield: «Empty repo — we'll pick the foundation together (a few questions), then `scaffold` builds the skeleton. Road ahead: survey (now) → roadmap (if you have an idea brief) → scaffold → specify.»

### Brownfield path (existing code)

2. **Read authored docs first.** Any hand-maintained architecture doc / root `CLAUDE.md` / ADRs → authoritative input; reconcile with it, never overwrite.
3. **Scan via explorer.** Dispatch the [`explorer`](../../agents/explorer.md) agent — `subagent_type: "foresdd:explorer"` (`haiku`/`low`, clean-isolated per [`../allocations/agent-roster.md`](../allocations/agent-roster.md)): «Report (a) language + frameworks + versions, (b) top-level module layout + per-module layers, (c) layering / wiring conventions, (d) datastores + access, (e) inter-module comms, (f) cross-cutting conventions (errors, IDs, tests, migrations) with one cited example each, (g) 2–3 representative features as precedents, (h) **if a frontend exists** — the component library / design system, design tokens (colors/spacing/typography), styling approach (Tailwind / CSS-modules / styled-components / …), shared UI primitives, and a representative screen/component as the UI precedent to reuse.» Large repo → fan out per subtree. (Fallback `subagent_type: "Explore"`.) Item (h) is the **reuse invariant's source**: the §Frontend / UI foundation section it fills is what `design` / `tasks` / `implement` later **compose against instead of reinventing** — new UI work reuses these components / tokens / the single styling approach, and `review` flags from-scratch UI that duplicates them. An incomplete inventory here silently licenses a second design system downstream.
4. **Synthesize + stamp + validate + write.** Copy [`./templates/architecture-map.md`](./templates/architecture-map.md) to `docs/architecture-map.md` as soon as the first explorer report lands (a stale map is edited in place, never re-bootstrapped), and write each section **as it is synthesized** — per fanned-out subtree too — never the whole map at the end ([`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) §1). Fill it (C4 of what exists, module inventory, cited conventions, datastores, **the Frontend / UI foundation if a frontend exists**, precedent guide, constraints) with real `file:line` anchors. **Fill the machine-readable frontmatter keys** (`language`, `build_cmd`, `test_cmd`, `lint_cmd`, `migration_tool`, `frontend`) from the explorer's findings — a key with no evidence stays `""` (unknown), **never a guess**; `implement`'s command-detection cascade reads `test_cmd`/`lint_cmd` from here. Record `updated_at` + `reflects_commit: <short HEAD>`. **Validate the C4 Mermaid per [`../allocations/mermaid-check.md`](../allocations/mermaid-check.md)** (the structural lint script, plus a full `mmdc` parse when installed; fix before committing). Then the **structural self-check** (per [`../allocations/self-check.md`](../allocations/self-check.md)) — re-read the map from disk and verify: (1) every machine key holds an explorer-backed value or the explicit `""`; (2) every convention line cites a file that exists; (3) the C4 validated; (4) `reflects_commit` = current short HEAD.
5. **Owner confirm (the map reflects reality).** Before committing, summarize the map **in prose** — stack, the modules found, the 3–4 conventions a new feature most needs to match, the frontend foundation if any, and every machine key left `""` (unknown) — never the raw Mermaid. Then one `AskUserQuestion`: «Does this match how the system really works?» → **Looks right** / **Something's off** (free text). A correction is checked against the code (a scoped re-read, not a re-scan) before it lands in the map; one that can't be cited goes to §Constraints & known tech-debt marked *(owner-stated)*, never as a fake citation. A deliberate refresh of an already-confirmed map with no new modules may skip the question — say so in one line. Only then commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md): `survey: architecture-map.md (reflects <commit>)` (a failed self-check → no commit). Then **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) — *What I did* (incl. the commit SHA and which scan mode ran: full / incremental) + *Review* (`docs/architecture-map.md`) + *Run next*, picked from what is on disk: **`docs/idea-brief.md` present and no `docs/roadmap.md`** → `/clear`, then `/foresdd:roadmap` (with the skip line «or `/foresdd:specify <slug>` to go straight to one feature»); **`docs/roadmap.md` present** → `/clear`, then `/foresdd:specify <slug>` for its first unblocked step, named the way the roadmap names it; **neither** → `/clear`, then `/foresdd:specify <slug>`, with the skip line «or `/foresdd:interview` first if the idea itself is still fuzzy». (The greenfield path emits its own handoff in G6 — forward to `/foresdd:roadmap` when a brief exists and no roadmap yet, else to `/foresdd:scaffold`.)

### Greenfield path (empty repo) → [`./references/foundation.md`](./references/foundation.md)

(Numbered G2–G6 because step 1 above — settings + mode detection — is shared by both paths.)

G2. **Calibrate to the person.** One opening `AskUserQuestion` to gauge how the user wants to engage — «pick good defaults, I'll confirm» / «walk me through each choice with explanations» / «let me choose each piece, keep it terse». This sets the dialogue's depth + phrasing (junior → defaults + glossed explanations per [`../allocations/style.md`](../allocations/style.md); senior → terser, more control). Not a product brief. **Skip the question when the user already said it** («just use defaults», «I want to pick the stack myself», a stated stack + layout): name the depth you took from their words in one line and move on. Either way, add: «say "explain more" or "just pick" at any point to switch».
G3. **Intent (short).** What the project is + the kind of capabilities it'll have (e.g. «HTTP API» / «CLI» / «web app»). Enough to choose an architecture — deliberately NOT the feature briefing (that's `specify`, per feature). **Read `docs/idea-brief.md` first if it exists** ([`interview`](../interview/SKILL.md) writes it): its raw-idea and problem sections already answer this, so restate the intent back in one line for confirmation and move on. Only what the brief leaves open becomes a question — 1–3 of them, never a re-ask of something already on disk.
G4. **Pick the foundation, defaults-heavy.** At the calibrated depth, choose: stack (language/framework/datastore), architectural style (e.g. hexagonal modules), folder/module structure, data/persistence approach (migration tool, ID strategy), core conventions (errors, tests, CI). Recommend a coherent default set; the user confirms or adjusts. From the first confirmed pick, `docs/architecture-map.md` exists on disk (template copied, `mode: greenfield-bootstrap`) and each pick lands in its section **as soon as it is confirmed** ([`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) §1). Choice menus + defaults → [`./references/foundation.md`](./references/foundation.md).
G5. **Fix the foundation.** Complete `docs/architecture-map.md` as the **established foundation** (mark `mode: greenfield-bootstrap`; the C4 is the *target* baseline) + spawn **foundational ADRs** in `docs/adr/` for the irreversible picks (stack, module style, persistence) — each ADR written to disk as it is decided. **Fill the machine-readable frontmatter keys** from the chosen foundation (`language`, `build_cmd`, `test_cmd`, `lint_cmd`, `migration_tool`, `frontend`) — here they encode the *decided* toolchain; anything not yet decided stays `""`. Record `reflects_commit`. **Validate the C4 Mermaid per [`../allocations/mermaid-check.md`](../allocations/mermaid-check.md)** and run the same step-4 structural self-check — nothing is committed before it passes.
G6. **Emit the scaffold plan + hand off.** Write a scaffold `tasks.json` (the skeleton: folder/module structure, a baseline module, the test harness, migration tooling, CI, a `CLAUDE.md`/rules doc) per the contract in [`./references/foundation.md`](./references/foundation.md). Each task's DoD anchors on the **skeleton smoke test** — «the project builds + boots + the empty test suite runs + the migration tool runs» (canonical in [`../scaffold/SKILL.md`](../scaffold/SKILL.md)). Then commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — one commit per document: `survey: architecture-map.md (greenfield foundation)`, **each** ADR on its own (`survey: ADR-NNNN <title>`), `survey: _scaffold tasks.json`. Then **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) — *What I did* (incl. the commits with short SHAs) + *Review* (`docs/architecture-map.md`, `docs/adr/`, `docs/features/_scaffold/tasks.json`) + *Run next*, picked from what is on disk: **`docs/idea-brief.md` present and no `docs/roadmap.md`** → `/clear`, then `/foresdd:roadmap` (it cuts the idea into steps with the skeleton as step 1, and its own handoff then gives `/foresdd:scaffold`), with the skip line «`/foresdd:scaffold` also runs now — it reads only the map and `_scaffold/tasks.json`, not the roadmap»; **otherwise** → `/clear`, then `/foresdd:scaffold` (it materializes the skeleton; the per-feature flow starts afterwards with `/foresdd:specify <slug>`). One order across the pipeline: interview → survey → roadmap → scaffold → specify.

## Definition of Done

- `docs/architecture-map.md` exists with `updated_at` + `reflects_commit`; an authored doc (if any) was reconciled, never overwritten.
- **Brownfield:** C4 of what exists + module inventory + cited conventions + precedent guide, real anchors (no placeholders); the owner confirmed the prose summary (or corrected it) before the commit.
- **Greenfield:** foundation fixed (stack/structure/data/conventions) at the user's calibrated level + foundational ADRs + a scaffold `tasks.json` whose tasks carry the skeleton smoke-test DoD, ready for `/foresdd:scaffold`.
- The step-4 **structural self-check** passed ([`../allocations/self-check.md`](../allocations/self-check.md)): machine keys explorer-backed or explicitly `""`, convention citations resolve, C4 validated, `reflects_commit` current; its result is reported in the handoff.

## Anti-patterns

- **Re-scanning the repo in every downstream skill** — the point is to scan once; others read the map (drift detection is the only re-read, of real domain files).
- **Overwriting a hand-maintained `docs/architecture.md`** — survey writes its own map and reconciles.
- **A map with no `reflects_commit`** — it silently rots; nobody knows it's stale.
- **Greenfield: a full product brief.** The foundation session picks the *architecture*, not the features — the idea/briefing is `specify`'s job, per feature. Keep it to intent + foundation choices.
- **Greenfield: ignoring the person's level.** A junior gets defaults + plain-language explanations; a senior gets control + terseness. One calibration question sets this — don't fire a senior-level wall of choices at a first-timer.
- **Placeholders / guessed layout** — cited, or `""` (unknown) for a machine key / an explicit «not found» in prose; a fictional map is worse than none.
- **Committing a brownfield map the owner never saw.** The scan can be confidently wrong about intent (a legacy module, a convention being phased out); step 5's one confirm is cheaper than every downstream skill building on a misread.

## References & template

- [`./references/foundation.md`](./references/foundation.md) — greenfield: the calibration question, level-adaptive depth, the stack/structure/convention choice menus + defaults, foundational-ADR list, and the scaffold `tasks.json` contract.
- [`./templates/architecture-map.md`](./templates/architecture-map.md) — output scaffold (same file for current OR foundation; a `mode:` marker distinguishes).
- [`../allocations/agent-roster.md`](../allocations/agent-roster.md) — the explorer contract.
