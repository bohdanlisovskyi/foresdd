---
name: specify
model: inherit
effort: high
agents: [critic, researcher, strategist, analyst, devils-advocate, explorer]
description: >
  Use to turn a raw feature idea into a reviewed spec.md — a lightweight Socratic interview front
  (capture the idea, deep-dive the problem) merged with a full product spec (context, goals, user
  stories, acceptance criteria, NFRs, KPIs). Triggers on "specify {slug}", "spec for {slug}",
  "write the spec", "capture this idea", "draft requirements for {slug}", "/foresdd:specify {slug}".
  Captures the idea first, then confirms the interview depth (easy/medium/hard) + size + route in
  one calibration question, drafts from templates/spec.md, validates each acceptance criterion
  Socratically, runs a clean-context critic, then writes docs/features/{slug}/spec.md. The ideation
  analyses (competitive research, strategic approaches, multi-perspective review, devil's-advocate)
  run as named subagents gated by the depth dial — easy skips them, hard runs the full suite.
  Baseline mode ("baseline {area}", "spec the existing {area}", "/foresdd:specify {area}
  --baseline") instead captures what EXISTING code already does as an owner-confirmed spec
  (kind: baseline, observed ACs with code evidence) so a later change in a pre-SDD area has
  something to be a delta against.
---

# Skill: specify

Turns a one-line idea into a reviewed `spec.md`: a lightweight interview captures and stress-tests the idea, then the skill drafts a product spec (context → goals → user stories → acceptance criteria → NFRs → KPIs), validates it Socratically, and runs a clean-context critic before writing. Less typing, more reviewing. This file is the spine; detail lives in `references/`.

The Socratic machine, the critic, and the T-shirt sizing matrix are **shared** — this skill keeps only its deltas:
→ [`../allocations/socratic-loop.md`](../allocations/socratic-loop.md) · [`../allocations/critic.md`](../allocations/critic.md) · [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md) · [`../allocations/style.md`](../allocations/style.md)

Depth governs question volume + autonomy (and which ideation analyses run) → [`../allocations/interview-depth.md`](../allocations/interview-depth.md).

## Owner

PM + Tech Lead (co-authors). PM drives goals / non-goals / KPIs; Tech Lead drives context patterns and the acceptance-criteria coverage.

## Inputs

- `<slug>` — kebab-case feature slug (in baseline mode: the **area** slug, e.g. `orders`).
- `--baseline` — optional; run [baseline mode](#baseline-mode--specifying-code-that-already-exists).
- (Optional) `CONTEXT.md` — the two-level glossary: read **both** repo-root (project-wide) and `docs/features/<slug>/CONTEXT.md` (feature-scoped); per-feature wins on conflict → [`../glossary/SKILL.md`](../glossary/SKILL.md). If present, its roles/terms are canonical and override anything that contradicts them.
- `docs/features/<slug>/.size` + `.route` — **read if present; established here if absent** (step 1 classifies + writes them), so downstream stages never silently default to M. `tshirt-size` re-classifies when scope changes.
- `docs/features/<slug>/.depth` — reused if present (normally written by this skill's step 1).
- (Optional) `docs/idea-brief.md` — read before repeating discovery; identity, readiness and reuse
  follow [`./references/brief-reuse.md`](./references/brief-reuse.md). A brief is not mandatory.
- (Optional) `docs/architecture-map.md` (from `survey`) — makes the spec architecture-aware.
- (Optional) prior notes / a reference module / a ticket the user already has.

## Baseline mode — specifying code that already exists

For a repo that adopted foresdd mid-life. A change about to land in an area that was built before foresdd has no spec to be a delta against, so `fix` can't call a bug a regression and `review` can't check the old behaviour survived. Baseline mode records what the code does **today** as `docs/features/<area>/spec.md` with `kind: baseline` — every §5 AC **observed** (backed by a `file:line` in §9 Evidence) and confirmed by the owner as Intended / Known defect / Not sure. It is lazy: one area, right before the first change touches it.

- **Entry:** `--baseline`, a baseline trigger phrase, or the step-1a offer below.
- **Protocol:** five phases (Capture & calibrate → Scan → Draft → Owner confirm → Critic & commit) instead of seven — no ideation, no size/route, no 5-coverage-type floor (a missing type becomes a §8 finding about the code, never an invented AC). Template [`./templates/spec-baseline.md`](./templates/spec-baseline.md); full detail → [`./references/baseline.md`](./references/baseline.md).
- **After:** the change gets its own slug; its spec carries `extends: <area>` and writes only the delta. `design`, `tasks` and `implement` refuse a `kind: baseline` spec.

The rest of this file describes the normal (new-feature) run.

## The run at a glance — the phase map

The user always sees where they are. specify runs **seven phases**; the numbers are the protocol step numbers below.

```
1 Capture & calibrate → 2 Deep-dive → 3 Ideation → 4 Sources → 5 Draft → 6 Validate §4–§7 → 7 Critic & commit
```

- **Run plan (once, at the end of step 1).** Right after calibration, print the map with this run's values — depth, size/route, what step 3 will dispatch (or «skipped at easy»), and the expected effort: the «Typical effort per stage» cell for the chosen depth from [`../allocations/interview-depth.md`](../allocations/interview-depth.md). Mark a phase that will be skipped or reused with `↷` and a 3–6-word reason («↷ reused from brief»). Example:

  ```
  specify — checkout-v2 · depth medium · size M / standard
  1 Capture & calibrate ✓ → 2 Deep-dive ▶ → 3 Ideation (researcher + devils-advocate) → 4 Sources → 5 Draft → 6 Validate §4–§7 → 7 Critic & commit
  Expect: every real decision asked, batched ≤4 per round — usually 3–5 rounds before the draft, then one walk per section.
  ```

- **Phase banner (every phase start).** One line, before anything else in that phase: `▸ specify <n>/7 · <phase> — next: <next phase>` (e.g. `▸ specify 3/7 · Ideation — next: Sources`). A skipped phase still gets its banner with the reason (`▸ specify 3/7 · Ideation ↷ easy depth — next: Sources`), so the count never jumps.
- **Question marker (steps 1–4).** Every `AskUserQuestion` before the Socratic walk starts its question text with `specify <n>/7 <phase> · question <k>/<total in this phase>` and its `header` chip carries `<n>/7 · <k>/<total>`. When the total is not known up front (a deep-dive whose answers spawn follow-ups), show `<k>/~<estimate>`. From step 6 on, the Socratic loop's own marker takes over ([`../allocations/socratic-loop.md`](../allocations/socratic-loop.md) §Cadence).
- **Waiting is announced.** Before a subagent dispatch (steps 3 and 7), say what runs, why, and that no input is needed: «Running researcher + devils-advocate in parallel (competitive scan + failure modes) — usually a minute or two; nothing needed from you.» When it returns, give a 2–4-line digest before the next question.
- **Headless / no-tool runs** print the banners and run plan the same way; only the questions change form ([`../allocations/fallbacks.md`](../allocations/fallbacks.md)).

## Protocol

1. **Capture & calibrate.** Steps 1a–1d, in order. The idea comes **before** any calibration question, so depth, size and route are proposed *from* it instead of guessed blind.

   - **1a — Setup (no questions).** **Ensure the settings file (first thing, after this skill's own gate).** If `.claude/sdd.local.md` is absent, create it from the canonical template and patch `.gitignore`; if it exists, read it and never overwrite → [`../allocations/settings-file.md`](../allocations/settings-file.md) (creating is unconditional; **changing values is only ever offered by [`config`](../config/SKILL.md)**; say the canon's one-line creation notice only when the file was just created). Load `## Glossary` from **both** `CONTEXT.md` levels as session state (per-feature wins). If `docs/architecture-map.md` exists, read it — it informs §1 Context, §2 Goals and §3 Non-goals (what the existing system already does / can't do); absent → note «no architecture map — `survey` would make the spec architecture-aware» for the handoff and proceed. **Do not leak the map's tech into §5 AC.** Read any existing `.depth` / `.size` / `.route`.
     **Pre-SDD area? (brownfield, no `--baseline`).** If the idea is a change to an existing capability (the map's module inventory or a quick grep shows the code it changes) and **no** `docs/features/*/spec.md` owns that area, ONE `AskUserQuestion`: **Capture the baseline first** (run baseline mode for `<area>` now; this change spec follows in the next run with `extends: <area>`) · **Spec only the change** (proceed; the handoff notes that no baseline exists) · **Stop**. «(Recommended)» goes on Capture-first when the change **alters** existing rules, on Spec-only when it is a pure addition that leaves today's behaviour alone; the recommended option is listed first. When a baseline for the area exists (`kind: baseline`), set `extends: <area>` in the frontmatter, read its §4/§5 as the current behaviour, and draft only the delta — an altered AC names the baseline AC it supersedes ([`./references/baseline.md`](./references/baseline.md) §How downstream stages use a baseline).
     **Existing spec?** If `docs/features/<slug>/spec.md` already exists, never overwrite it silently. Uncommitted changes → the **Resume / Restart** question from [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) §1. Committed and clean → ONE question: **Revise this spec** (load it as the baseline; later phases walk only what the user wants changed, and filled sections count as resolved) · **Restart from the template** (the old version stays in git history) · **Stop — sharpen it with clarify instead** (emit the handoff naming `/foresdd:clarify <slug>`; nothing written).
   - **1b — Capture the idea.** Apply [`./references/brief-reuse.md`](./references/brief-reuse.md) first: a usable `docs/idea-brief.md` supplies the idea, problem, actors and accepted decisions. Otherwise reuse the user's own words when the invocation already carries the idea — never ask them to repeat it. Only when there is no idea at all, ask for it in plain text, in 1–3 sentences (an open question, not a menu). Echo the captured baseline back in one line so the user can correct it before anything is built on it.
   - **1c — Calibrate (ONE `AskUserQuestion` call, ≤2 questions).** Infer the four size signals from the idea per [`../tshirt-size/SKILL.md`](../tshirt-size/SKILL.md) step 2 (≤10-word evidence note each; *unknown* rather than a guess). Then bundle whatever is still unresolved into one call, each question phrased per [`../allocations/style.md`](../allocations/style.md):
     - **Depth** — only when neither `--depth=` nor `.depth` resolved it ([`../allocations/interview-depth.md`](../allocations/interview-depth.md) resolution order). «(Recommended)» = `interview_depth` from settings (else medium; `easy` when an existing `.route` is `quick`). Each option says what that level will do to *this* run — name the step-3 agents it will dispatch.
     - **Size + route** — only when `.size` is absent: the tshirt-size **confirm question** (step 4 of its protocol — `Yes — <size>, <route>` (Recommended) · `Yes, but route <alt>` · `Different size` / `XL` · `Adjust signals`), its rationale listing the four inferred answers. When any signal is *unknown*, ask the four-signal call first instead (inferred answers pre-selected) and confirm in a second call — the only case calibration takes two round-trips.
     - When `.depth` already resolved to `easy`, don't ask size + route: take the matrix default from the inferred signals and record it as an assumptions-ledger entry (`high` risk when a structural signal was *unknown*).
     Write `.depth`, `.size` and `.route` the moment they are answered. Never lock a size without confirmation (a ledgered size at easy is confirmed by the ledger review).
   - **1d — Bootstrap + run plan.** Copy [`./templates/spec.md`](./templates/spec.md) to `docs/features/<slug>/spec.md` (frontmatter stamped — `feature_size` mirrors `.size`; sections still placeholders; skipped on **Revise**) — from here on every resolved section lands in that file immediately → [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md). Then print the **run plan** (phase map above).

2. **Deep-dive.** Brief reused → ask only the specification gaps [`./references/brief-reuse.md`](./references/brief-reuse.md) names. Otherwise a Socratic deep-dive across problem clarity / success criteria / constraints / strategic fit, batched 2–3 per call — volume scales with depth (easy: only the few un-inferable ones, the rest ledgered; medium: 3–5; hard: walk every angle, foreground each trade-off). Phrase every question per [`../allocations/style.md`](../allocations/style.md).
3. **Ideation suite (reuse first, then depth-gated subagents).** Apply [`./references/brief-reuse.md`](./references/brief-reuse.md) before dispatch: reuse covered signals at every depth, run only remaining/reopened gaps, and never manufacture absent RICE/matrix outputs. Without a usable brief, run the ideation analyses as named-subagent dispatches gated by the **interview-depth dial** (size as a secondary trimmer) → [`./references/ideation.md`](./references/ideation.md): **easy** → skip the suite (deep-dive only; the chosen approach is recorded as a ledger assumption); **medium** → `researcher` (`foresdd:researcher`, competitive/web) + `devils-advocate` (`foresdd:devils-advocate`, failure-mode mode); **hard** → full suite `researcher` + `strategist` (`foresdd:strategist`, 3 approaches) + `analyst` (`foresdd:analyst`, multi-perspective) + `devils-advocate`, then the Claude-proposed RICE/feasibility confirm. Analyses stay **product-level** (no tech names — that's `design`); the confirmed recommendation becomes §1 ¶3. Dispatch with `subagent_type: "foresdd:<name>"` per [`../allocations/agent-roster.md`](../allocations/agent-roster.md) (`general-purpose` fallback); `researcher` needs web — accept its `RESEARCH_LIMITED` output as a noted gap if web is unavailable.
4. **Sources — only the channels that exist.** Detect which extra channels are actually available before asking: reference-module code (the repo has source beyond docs), project docs (`docs/` holds more than this feature), MCP-Atlassian (its tools are present in this session), a knowledge-base the user named. **None available → skip the question** (banner says why). Otherwise ONE multi-select `AskUserQuestion` listing only the available channels + `None`, each description naming what was detected («`docs/` has 14 files, incl. `docs/billing/`»). For each picked channel ask the **specific** path/query in the same follow-up call (≤4 questions) — no silent broad scans. At `easy`, still ask (reading sources needs paths), but `None` is «(Recommended)» unless the idea names a module.
5. **Read the template + draft §1–§8.** Read [`./templates/spec.md`](./templates/spec.md) (its `<!-- instruction -->` comments are the per-section contract). Draft per [`./references/draft-generation.md`](./references/draft-generation.md): per-section sources, the **5 AC coverage types** (happy / error / authorization / domain invariant / cross-context), size-scaled counts (never filler to hit a number), and the **stack-agnostic forbidden-token** rule for acceptance criteria. §1–§3 (not per-item walked) go into `spec.md` as soon as they are drafted — show them in one message and tell the user they can edit them inline or in their editor.
6. **Socratic validation.** Walk §4 US → §5 AC → §6 NFR → §7 KPI with the shared 4-state machine (per-decision question volume scales with the depth dial — at easy, the un-asked decisions land in the assumptions ledger for a batch veto). Specify delta → [`./references/socratic.md`](./references/socratic.md): a new AC is added via the built-in «Other» free-text answer (AC questions keep the 4 options — the `AskUserQuestion` max); the §5 coverage gate enforces **two floors** after drops/OQ-migrations — (a) ≥1 AC of each of the 5 coverage types, and (b) **≥1 AC per retained §4 user story** (regenerate/add a replacement if a type *or* a user story is left empty). **Both are floors, not dials — enforced at every depth;** only the question volume scales. The (b) floor closes the §4→§5 link so the downstream `sequences` use-case coverage + `review` trace can't be undermined by a user story that lost its only AC. Maintain the edits-log. Write each section into `spec.md` right after its last decision resolves (§8 gets each `save_as_oq` row as it happens; accepted ledger entries land in §8.1 Assumptions after the ledger review). End with the shared **pass summary** before the critic.
7. **Critic + self-check + commit.** Dispatch the [`critic`](../../agents/critic.md) agent — `subagent_type: "foresdd:critic"` (**model per `judgment_model`**, effort `high` — `xhigh` on L/XL via `CLAUDE_CODE_EFFORT_LEVEL`; clean-isolated context per [`../allocations/agent-roster.md`](../allocations/agent-roster.md)) — with the specify delta in [`./references/critic.md`](./references/critic.md) (over [`../allocations/critic.md`](../allocations/critic.md)) — inline the edits-log + current owner corrections, it Reads `docs/features/<slug>/spec.md` from disk + both `CONTEXT.md` levels + the idea source (including the reused brief) itself and checks preservation of accepted constraints and evidence limits. Resolve the findings per the shared resolution flow (summary table → batched `AskUserQuestion` with before/after previews, options per fix-type; Override-with-rationale → §1 ¶4 bullet; at `easy` mechanical fixes auto-apply; one bounded re-check). Patch `spec.md` on disk with every accepted revert/amendment as it is resolved. Run the forbidden-token regex scan over the file as the F6 backstop (glossary already reconciled in-flow). **Set `reviewers`** in the frontmatter: `Tech Lead` always, plus `Security Lead` exactly when §6.1 says `Security review: Required`. **Register on the roadmap:** in `docs/roadmap.md` (via `roadmap`) set the matching step's `Status: spec'd` and link this feature folder; no matching step → append one (source anchor = this spec). (If there's no roadmap yet, skip — it's optional.) **Commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md)** — only after the critic + F6 scan pass; one commit per document: `specify: <slug> spec.md`, `specify: <slug> .size+.route` (one commit; `.depth` rides in the first commit), `specify: <slug> CONTEXT.md` (each glossary file the in-flow reconciliation changed), `specify: roadmap.md` — skipping any that didn't change. Then **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) — *What I did* (incl. depth, size/route, and the counts from the pass summary: N US · N AC · N NFR · N KPI · N open questions · N assumptions) + *Needs your attention* (every §8 open question with owner + due, every `high` assumption kept in §8.1, a missing architecture map) + *Review* (`spec.md` — name the sections to eyeball first: §5 AC and §8; `.size`, `.route`) + *Run next* — **resolve the next stage per `.route`** (the Routes table in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md); route-resolved variant in handover.md): forward `/foresdd:clarify <slug>`; `clarify`'s N/A condition = **zero §8 open questions and no AC flagged ambiguous**, skip target `/foresdd:ux-flows <slug>` (on `quick` — auto-skip with the reason + inverted `↳ or`; on `standard` — offer the `↳ or`; on `full` — no skip line). When clarify is legally skipped, **carry the next condition forward**: evaluate `ux-flows`' N/A condition too (no human-facing UI — every §4 actor a system/service, or the repo has no UI at all, per [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md)) → holds ⇒ the skip target becomes `/foresdd:design <slug>`. (If `critic` is unavailable, fall back to a `general-purpose` Agent with the same delta.)

## Throughout the run (standing rules)

- **Reconcile the glossary in-flow (a hard rule, at every depth).** On every new or unknown domain term that surfaces in the interview or the draft, invoke `glossary <slug>` for it **immediately** — compare it against `CONTEXT.md` and add/update the definition before continuing. By the time the spec is written, every §4 role and §5 domain term is already glossary-canonical; the glossary is never a deferred batch. (Plan-mode nuance: still decide add/update per term in-flow; if writes are blocked until the spec write-point, persist the reconciled terms together with the spec, but never skip the per-term compare.)
- **Depth can change mid-run** — «deeper» / «faster» / a level name at any question, per [`../allocations/interview-depth.md`](../allocations/interview-depth.md) §Changing depth mid-run. Re-print the phase map with the new values when it happens.
- **Progress is visible** — the phase banners, question markers and run plan above are not optional decoration; a question without its marker has regressed.

## Definition of Done

- `docs/features/<slug>/spec.md` written; all sections filled (or `<!-- N/A: reason -->`). Counts follow the template's size-scaled guidance — no section padded with filler to reach a number.
- `docs/features/<slug>/.size` **and `.route`** exist after this stage (read if present, else classified + written here) — the backbone no longer reaches `design`…`plan-tests` on a silent M default, and every handoff resolves per a real route.
- §5 holds ≥1 AC of each of the 5 coverage types after drops/OQ-migrations, **every §4 user story has ≥1 AC** (the use-case floor — no retained US left with zero ACs), and **0 forbidden tokens** (HTTP verbs / URL paths / status-code numerics / `module.error_name` strings / JSON fragments / SQL constructs).
- §4 roles match the `CONTEXT.md` glossary exactly (no invented `user`/`admin`).
- §8 Open Questions each carry owner + due (no lone «TBD»); zero open questions is written as `None.`, not invented. §8.1 holds every assumption the spec relies on that the user accepted rather than answered (or `None.`).
- `reviewers` frontmatter matches §6.1's security-review verdict.
- Edits-log maintained; critic ran on the post-Socratic `spec.md` read from disk; every finding resolved or overridden.
- `spec.md` was bootstrapped in step 1 (or revised in place) and filled section by section; after the self-check, one commit per changed document (`spec.md`, `.size`+`.route`, `CONTEXT.md`, `roadmap.md`), SHAs listed in the handoff — per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md).
- The run plan was printed after calibration and every phase opened with its banner.
- The step-7 critic + the forbidden-token regex backstop are this skill's **structural self-check** ([`../allocations/self-check.md`](../allocations/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **Calibrating before the idea is known.** Asking depth or size before the user has said what the feature is forces a blind guess; capture first (step 1b), then propose.
- **Silent progress.** Long stretches of questions or subagent waits with no banner, marker or «nothing needed from you» line — the user can't tell how much is left or whether the run is stuck.
- **Inventing behaviour in a baseline.** An observed AC without a code anchor, an AC added to satisfy a coverage type the code lacks, or a target the code never set — a baseline is evidence, not aspiration.
- **Back-filling every area up front.** Baselines are captured lazily, per area, when a change is about to touch it.
- **Overwriting an existing spec.** A re-run that re-bootstraps over a committed or in-progress `spec.md` without the Resume / Revise / Restart question.
- **Filler to hit a count.** Invented open questions, generic non-goals, an NFR row for a latency nobody will measure, user stories for glossary roles the feature never touches. Size-scaled guidance is a range, not a quota; the coverage floors are the only hard minimums.
- **Inventing owner answers.** Reuse confirmed brief/conversation answers; ask about missing consequential decisions. Repeating a settled interview is not required, and headless execution does not license new guesses.
- **Naming concrete technologies in §1–§3** (a specific datastore, broker, framework, or library). The spec is WHAT + WHY; technology choices belong to `design`.
- **Implementation leak in AC** — HTTP/status/error-code/SQL detail. That mapping lives in `api` and `decide-adr`.
- **Running the full ideation suite at `easy` depth** — over-production. The depth dial gates it (easy skips entirely; medium runs research + devil's-advocate; hard runs all). Feature size only *trims volume* within a level — it's no longer the gate.
- **Holding the whole spec in memory and writing it once at the end** — a lost session loses every decision. Bootstrap in step 1, write each section as it resolves.
- **Inventing competitors / RICE numbers** to fill the ideation pass. Better `N/A — internal tool` than fake research; accept the `researcher` agent's `RESEARCH_LIMITED` over fabricated rows.

## References & template

- [`./references/baseline.md`](./references/baseline.md) — baseline mode: scan, observed-AC contract, owner confirm, relaxed floors, critic delta, downstream use.
- [`./templates/spec-baseline.md`](./templates/spec-baseline.md) — baseline output scaffold (`kind: baseline`, §9 Evidence).
- [`./references/brief-reuse.md`](./references/brief-reuse.md) — reusing `docs/idea-brief.md`: identity, readiness, what to reuse, ideation reuse.
- [`./references/ideation.md`](./references/ideation.md) — depth-gated ideation orchestration: which named subagent (`researcher` / `strategist` / `analyst` / `devils-advocate`) runs at which level, what each returns, how outputs feed the spec.
- [`../allocations/interview-depth.md`](../allocations/interview-depth.md) — the easy/medium/hard dial resolved in step 1c (question volume, autonomy, which analyses run).
- [`./references/draft-generation.md`](./references/draft-generation.md) — per-section sources, size-scaled counts, 5 AC coverage types, stack-agnostic forbidden tokens.
- [`./references/socratic.md`](./references/socratic.md) — specify's delta over the shared Socratic loop.
- [`./references/critic.md`](./references/critic.md) — specify's delta over the shared critic (F6 = forbidden tokens).
- [`./templates/spec.md`](./templates/spec.md) — output scaffold; inline comments are the per-section generation contract.
