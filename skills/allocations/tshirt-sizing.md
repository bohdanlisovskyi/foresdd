# T-shirt sizing — XS/S/M/L/XL classification, routes, and artifact depth

> **Reference-only.** Not a skill. `tshirt-size` is the canonical owner of this file; every other
> skill reads it to decide how much of its artifact to produce (MVP vs Full), how deep to run its
> Socratic pass, and how its handoff resolves optional-stage skips.

**Contents:** [Classify](#how-to-classify-a-t-shirt-size) · [Routes](#routes--quick--standard--full-the-auto-router) · [Route cheat-sheet](#route-cheat-sheet--what-the-user-gets) · [N/A conditions](#the-na-conditions-the-fast-lane-table) · [MVP vs Full](#mvp-vs-full-artifact-set) · [Surfaces](#surface-count-is-a-second-scaling-axis) · [SAD](#sad-size-behaviour) · [Wrappers](#wrappers--gates)

## How to classify a T-shirt size

### The four signals

Every signal has exactly **four answers, one per column** — the answer *is* the class for that
signal (no overlaps, no gaps). `tshirt-size` asks the four in **one** `AskUserQuestion` call (four
questions, four options each), so the options below are the literal option labels.

| Signal | XS | S | M | L |
|---|---|---|---|---|
| **PR count** | 1 | 2–4 | 5–14 | 15+ |
| **Time to merge the main part** | ≤1 day | 2–7 days | 1–4 weeks | >1 month |
| **New module / new API / DB migration** | none | one of three | two of three | all three, or a new subsystem |
| **Breaking changes for consumers** | none | internal only (same team) | public consumers | public + cross-team coordination |

- **XS** — one PR, a day, nothing new, nothing breaks. (Typo, copy fix, config tweak.)
- **S** — a few PRs inside a week; at most one new thing (an endpoint, a small migration).
- **M** — a separate epic, up to a month; two new things or a public contract change.
- **L** — cross-module, over a month, several teams or public breaking changes.
- **XL** — L **plus** «needs its own roadmap» (a new subsystem). There is no XL column: XL is
  offered in the confirm question whenever the computed size is L (see below).

### Combining the signals — highest signal wins

1. **Size = the highest class among the four answers.** Predictable, and it never hides a risky
   migration or a breaking change behind three small answers.
2. **One permitted talk-down.** When exactly **one effort signal** (PR count or time) sits exactly
   **one** class above the other three, the proposal may drop one class — say it aloud: «S, not M:
   only the time estimate says M, and nothing new is built or broken». A **structural** signal
   (module/API/migration, breaking changes) is **never** talked down.
3. **XL** — when the result is L, the confirm question offers `XL — needs its own roadmap` as an
   option. Picking it is the only way to XL.

> **One-sentence rule.** If you hesitate between MVP and Full — start with MVP. Filling the empty
> sections of an artifact later is cheaper than discarding pre-built ones.

### Inferred signals (the one-click path)

When an idea, brief, or `spec.md` already exists, the skill **reads it first** and infers each
signal with a one-line evidence note. Then:

- **All four inferred with evidence** → skip straight to the confirm question; its rationale lists
  the four inferred answers («1 PR · ≤1 day · none · none → XS»). One click locks it. The
  `Adjust signals` option re-opens the four-question call.
- **Any signal unknown** → ask the four-question call, with each inferred answer as the first
  option marked `(Recommended)`; unknown signals have no recommendation.

Never lock a size without the user's confirmation — inference only pre-fills.

## Routes — quick / standard / full (the auto-router)

The **route** decides how the optional stages (`clarify`, `ux-flows`, `sequences`, `data-model`,
`api`, `screens`, `plan-tests`) are handled at each handoff. It lives in **`docs/features/<slug>/.route`** — one
line, plain text, exactly one of `quick` / `standard` / `full` (same discipline as `.size`: no
comments, no frontmatter — wrappers grep it cheaply). It is written by `tshirt-size` (the
canonical owner) and by `specify` step 1 when it classifies inline; the route **default derives
from the size** — **XS/S → `quick`, M → `standard`, L/XL → `full`** — and is confirmed together
with the size in the **same single `AskUserQuestion`** (the user may pick a different route than
the default; a `quick` L is legal, just loud).

| Route | Handoff behaviour at an optional stage |
|---|---|
| `quick` | the producing stage **evaluates the N/A condition itself** (table below): condition holds → **auto-skip** the stage, stating the reason in the handoff («auto-skipped `clarify`: zero §8 OQ»), and the `↳ or` alternative **inverts** — it now offers the *skipped* stage («run the full path»); condition does **not** hold → the stage is not skipped, normal forward handoff |
| `standard` | the handoff names the next stage and **offers** the skip as the `↳ or` alternative when the N/A condition holds; the **user** picks |
| `full` | no skip alternatives — every optional stage runs; the handoff never prints an `↳ or` skip line |

**Quick-route softenings** (in addition to the auto-skip): whichever stage asks the feature's one
depth question (normally `specify`; `design` when no `.depth` exists yet) recommends `easy` —
[`interview-depth.md`](./interview-depth.md); `plan-tests` always collapses to the inline `## Test plan`
in `spec.md`; `clarify` auto-skips when the spec has zero §8 open questions.

**Missing `.route`** → behave as `standard` and say so in the handoff —
«route standard (default — no `.route`; run `/foresdd:tshirt-size <slug>`)».

**Mid-flight override.** The route steers **handoffs only — it never makes a stage refuse**. To
change course: re-run `/foresdd:tshirt-size <slug>` (rewrites `.route`), or simply invoke a skipped
stage directly — it runs normally regardless of the route.

### Route cheat-sheet — what the user gets

The confirm question quotes the **«In one line»** cell for the proposed route, so the user knows
what they are agreeing to.

| Route | Default for | In one line | You will be asked |
|---|---|---|---|
| `quick` | XS / S | Shortest legal path — optional stages that don't apply are skipped for you, with the reason shown | the fewest questions; design defaults to easy depth |
| `standard` | M | Same stages, but every skippable stage is offered to you as a choice at its handoff | one skip/keep decision per optional stage that is N/A |
| `full` | L / XL | Every optional stage runs; nothing is skipped | the most questions; the full artifact set |

Every route keeps the never-skippable backbone (below), and every route still runs an optional
stage whose N/A condition does **not** hold — a `quick` XS with a schema change still gets
`data-model`.

### The N/A conditions (the fast-lane table)

Every condition is a **«skip when N/A»** condition, never «skip always»: an XS feature *with* a
schema change still runs `data-model` — on every route.

| Stage | Skip when (the N/A condition) | Who evaluates/offers it |
|---|---|---|
| `clarify` | the spec came out with **zero §8 open questions** and no AC was flagged ambiguous during specify | `specify`'s handoff |
| `ux-flows` | **no human-facing UI** — every spec §4 actor is a system/service (API-to-API, worker, scripted CLI), **or** the repo has no UI at all (`architecture-map.md` `frontend: ""` and no `docs/design-system.md`). `target_surfaces` doesn't exist yet at this point — the condition deliberately derives from the spec's actors + the repo signal; the **formal** surface declaration is made by `design`, which reads `ux-flows.md` as input | `clarify`'s handoff (`specify`'s when clarify was legally skipped) |
| `sequences` | **one actor and no multi-step runtime flow** — a single request/response or a pure rule change; nothing an `alt`-branch diagram would reveal | `design`'s handoff |
| `data-model` | **no schema change** — no new entity, column, index, or migration | `sequences`' handoff |
| `api` | **no contract change** — no new/changed endpoint, event, CLI command, or public signature (the skill also self-skips on «no external interface»). `api` **accepts a legally-skipped `data-model`** (no schema change) — it derives from the existing schema; its hard gate fires only when a schema change exists | `data-model`'s handoff |
| `screens` | **no UI surface declared** — `sad.md` frontmatter `target_surfaces` contains none of `web-frontend` / `mobile-app` / `desktop-app` | `api`'s handoff (carried forward when `api` is itself N/A) |
| `plan-tests` | never fully skipped — it **collapses to the inline `## Test plan`** in `spec.md` (cheap; always inline on `quick`); skip entirely only when every task's DoD already names its test | `tasks`' handoff |

**Never skippable — on any route:** `specify` (the spec is the trace anchor), `design` (declares
`target_surfaces` + the ADR gate), `tasks` (`implement` consumes `tasks.json`), `implement`,
`review`, `ship`. The shortest legal route is therefore
`specify → design → tasks → implement → review → ship` — a `quick` XS feature closes in one session.

When several consecutive stages are N/A, walk the conditions in order at each handoff and jump to
the first stage whose condition does **not** hold (skipping `sequences` moves its `data-model`
skip-question into `design`'s handoff, and so on) — on `quick` the stage walks them itself, on
`standard` it offers each hop as the `↳ or` alternative.

## MVP-vs-Full artifact set

Artifact depth ∝ feature size. XS/S → minimal set; M+ → full. «If N/A» rows follow the N/A table
above; whether the skip is automatic, offered, or suppressed follows the route.

| Artifact (skill) | MVP (XS/S) | Full (M+) |
|---|---|---|
| spec — `specify` | yes | yes |
| clarify pass — `clarify` | light; skipped if N/A (auto on `quick`, offered on `standard`) | yes |
| CONTEXT.md glossary — `glossary` | yes | yes |
| user flows — `ux-flows` | if human-facing UI | if human-facing UI |
| SAD (Arc42 12 §) + C4 L1/L2 — `design` | 12 sections walked, more `<!-- N/A -->` allowed | all 12 filled |
| ADRs (in `adr/`) — `design` / `decide-adr` | XS 0–2 · S 1–4 | M 5–12 · L/XL 10–15 |
| sequence diagrams — `sequences` | every AC covered, detail collapsed | as many flows as the user-stories/ACs need — never a cap |
| deployment view — `design` §7 | `<!-- N/A -->` if no infra change | yes |
| data-model + migrations — `data-model` | if DB touched | if DB touched |
| API contract (OpenAPI) — `api` | if the contract changes | yes |
| events — `api` | if async | if async |
| screens — `screens` | if a UI surface is declared | if a UI surface is declared |
| task breakdown + tasks.json — `tasks` | yes | yes |
| test-plan — `plan-tests` | inline in spec | separate file |
| implementation — `implement` | yes | yes |

ADR counts are **typical ranges, not quotas** — the blast-radius gate in `design` decides; a
count outside the range is a prompt to double-check, never a reason to invent or drop an ADR.

## Surface count is a second scaling axis

Size (XS–XL) is the *depth* dial; the number of **target surfaces** a feature declares (in `design`, written to `sad.md` frontmatter `target_surfaces` → [`./surfaces.md`](./surfaces.md)) is a second, *breadth* axis on the artifact set. Each surface adds its own work: a UI surface (`web-frontend` / `mobile-app` / `desktop-app`) adds the `ui` task layer, UI-driven §6 flows, and the component / visual-regression / e2e-through-UI test tiers; a `cli` / `worker` / `library-sdk` surface adds its own contract form + flows. So a multi-surface feature (`[backend-service, web-frontend]`) is genuinely **larger** than a single-surface one of the same XS/S/M class — no new column here, but expect more tasks, more flows, and more test rows per extra surface.

## SAD size behaviour

Even for XS/S, `design` walks all 12 Arc42 sections — consistency beats completeness theatre. Sections that genuinely don't apply get `<!-- N/A: <one-line reason> -->`. Common XS/S N/A patterns:

- §7 Deployment — `<!-- N/A: reuses existing deployment unit, no infra change -->`
- §6 Runtime — collapses to the **fewest flows that still cover every §5 AC** (often one flow with the error branches inline as `alt`, rather than separate failure-mode flows). Detail collapses; AC-coverage does not — `sequences` still maps every AC to a flow, a branch, or an explicit N/A even at XS/S.
- §11 Risks — one accepted-debt row, no medium/high risks.

Same skill, same template, smaller content footprint.

## Wrappers / gates

A skill that reads `.size` skips heavy sub-artifacts for XS/S (separate test-plan, deployment view, full ADR sweep). `specify` **establishes `.size` at the start of the backbone** (it classifies + writes it if absent), so later stages normally read a real size. A stage that *still* finds none (e.g. `design` run standalone, before `specify`) defaults to **M** (the safe over-production default) **and says so in its handoff** — «size M (default — no `.size`; run `/foresdd:tshirt-size <slug>`)» — never a silent assumption.
