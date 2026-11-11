# Baseline mode — capturing an existing area's behaviour as a spec

> Detail for [`../SKILL.md`](../SKILL.md) §Baseline mode. The spine says *when* baseline mode
> runs; this file holds *how*: the scan, the observed-AC contract, the owner confirm, the relaxed
> floors, and what downstream stages do with a baseline.

## Why it exists

A repo that adopts foresdd mid-life has features nobody ever specified. When a change lands in
one of them, three things break without a baseline:

- the change spec has nothing to be a delta **against** — it can only describe the new part;
- `fix` can never triage a bug as a **regression** (no AC exists to violate), only as a gap;
- `review` cannot check that the change **kept** the old behaviour.

A baseline spec records what the code does **today**, confirmed by its owner, so those three
links exist. It is captured **lazily** — one area, right before the first change touches it —
never as a big-bang backfill of the whole codebase.

## What a baseline is (and is not)

- **Is:** a `spec.md` with frontmatter `kind: baseline` and `status: Baseline`, written from
  [`../templates/spec-baseline.md`](../templates/spec-baseline.md), for an **area** slug (the
  module or capability as it exists — `orders`, not `orders-cancel`).
- **Is not:** a design input for new work. A baseline never goes down the backbone: `design`,
  `tasks` and `implement` refuse a `kind: baseline` spec and point at a change slug. It has no
  `.size` / `.route` (it plans no work) — only `.depth`.
- **Is not:** a wish list. Every §5 AC is **observed** — evidence-backed by code. Behaviour the
  owner *wants* but the code doesn't do belongs in the change spec, not here.

## Protocol (replaces specify steps 2–6)

Phase map in baseline mode — five phases, banner `▸ specify <n>/5 (baseline) · <phase>`:

```
1 Capture & calibrate → 2 Scan → 3 Draft → 4 Owner confirm → 5 Critic & commit
```

1. **Capture & calibrate.** Step 1a runs as usual (settings, glossary, map, existing-spec check).
   1b captures the **area** — which capability, which entry points — not an idea. 1c asks **depth
   only** (no size / route); depth scales the confirm volume in phase 4. 1d copies
   `spec-baseline.md` (not `spec.md`) and prints the run plan.
2. **Scan.** Dispatch [`explorer`](../../../agents/explorer.md) — `subagent_type:
   "foresdd:explorer"` (fallback `Explore` / inline per
   [`../../allocations/agent-roster.md`](../../allocations/agent-roster.md)) — with the area and,
   when present, the architecture map's module row for it. Ask for: the entry points (every way an
   actor reaches the area), each rule the code enforces (validation, permission check, invariant,
   call into another module) with `file:line`, the outcome on success and on each failure, and the
   **existing tests** that exercise each rule (`file:line` of the test case). Rules only — no
   design opinions, no «should».
3. **Draft.** Fill the template from the scan:
   - **§1** — what the area does and for whom, in product language; ¶2 «why a baseline now» = the
     change about to land (name the change slug when known). §1–§3 keep the usual no-technology rule.
   - **§4** — one user story per actor-facing capability the scan found. Roles from the glossary;
     an actor the glossary lacks → `glossary` in-flow (the standing rule still applies).
   - **§5** — one AC per rule the scan found, Given/When/Then in business language, heading
     `### AC-NN (US-XX) — <coverage type> · observed`. **The forbidden-token rule is unchanged** —
     the code's status codes, routes and error kinds are translated into what the actor observes
     («the system rejects the order and says the quantity must be positive»), never quoted.
   - **§9 Evidence** — one row per AC: the code anchor that enforces it and the test that pins it,
     or `unpinned`. File paths live **only** here, never in §5 text.
   - **§6 / §6.1 / §7** — only what the code or existing config states (a timeout, a rate limit, a
     permission check). No invented targets: a quality aspect the code doesn't fix is `N/A:
     not fixed by the current code` — the change spec sets targets.
4. **Owner confirm.** The scan says what the code does, not what anyone meant — this step is the
   whole point. Walk §5 in batches of ≤4 `AskUserQuestion` (phrasing per
   [`../../allocations/style.md`](../../allocations/style.md); marker
   `specify 4/5 Owner confirm · AC <k>/<n>`), each question showing the AC and its evidence anchor.
   Options:
   - **Intended** (Recommended) — the AC stays as written.
   - **Known defect** — the code does this but shouldn't. The AC stays (it is what the code does)
     with the marker `<!-- known-defect: <owner's one-line expectation> -->`, and a §8 row
     «AC-NN is a known defect — fix via `/foresdd:fix <area>` or the change spec» with owner + due.
   - **Not sure** — §8 open question with owner + due; the AC stays, marked `<!-- unconfirmed -->`.
   - **Out of this area** — drop it here (it belongs to another area's baseline).
   «Other» lets the owner reword. At **easy**, ACs whose evidence includes a pinning test are
   ledgered as Intended (batch veto at the end) and only the `unpinned` ones are asked; at
   **medium/hard** every AC is asked. Write §5 and §9 to disk as each batch resolves.
5. **Critic + commit.** The critic runs with the baseline delta below. Commit per
   [`../../allocations/write-and-commit.md`](../../allocations/write-and-commit.md):
   `specify: <area> baseline spec.md` (with `.depth`), plus `specify: <area> CONTEXT.md` when the
   glossary changed. No roadmap registration (a baseline is not a step).

## Floors — what changes and what doesn't

| Rule | Normal spec | Baseline |
|---|---|---|
| ≥1 AC per coverage type | hard floor | **not a floor** — a missing type is a *finding about the code*, written as a §8 row («no authorization check found for <capability> — owner: …, due: before the change's design»), never an invented AC |
| ≥1 AC per §4 user story | hard floor | hard floor (a capability with no observable rule is not a user story) |
| Forbidden tokens in §5 | zero | zero |
| No technology names in §1–§3 | yes | yes |
| Every AC has evidence | — | **hard floor** — a §9 row with a real `file:line`; no evidence → the AC is dropped |
| NFR numeric targets | required per row | only numbers the code fixes; else `N/A` |

## Critic delta (over [`./critic.md`](./critic.md))

- `{{ARTIFACT_NAME}}` = "Baseline spec (observed behaviour of an existing area)".
- `{{UPSTREAM_FILES}}` adds every `file:line` in §9 — the critic opens them and checks each AC
  matches what the anchored code does (**F1 for baselines: an AC the code does not support is a
  `must` finding**). Drop the brief-preservation and approach-drift probes.
- `{{F5_FLOOR}}` = the Baseline column above: every AC has a §9 row, every §4 US has an AC, a
  missing coverage type has its §8 row, no `<placeholder>` left, no invented NFR number.
- `{{F6_RULES}}` = unchanged (forbidden tokens in §5, technology names in §1–§3).

## Handoff

*What I did* — area, N US · N AC (N intended · N known-defect · N unconfirmed) · N unpinned ·
N coverage gaps; the commits. *Needs your attention* — every known defect, every unpinned AC,
every coverage gap. *Run next* — `/clear`, then `/foresdd:specify <change-slug>` (the change
spec picks up `extends: <area>` itself); `↳ or /foresdd:fix <area> <symptom>` for a known defect.

## How downstream stages use a baseline

- **specify (normal mode)** — a change spec whose area has a baseline sets frontmatter
  `extends: <area>`, reads the baseline's §4/§5 as the current behaviour, and writes only the
  delta. An AC the change *alters* names the baseline AC it replaces («supersedes `<area>`
  AC-03»); everything else in the baseline is implicitly preserved.
- **design** — reads the extended baseline's §5 + §9 next to the architecture map: it is the
  as-is behaviour the SAD must keep.
- **tasks** — for every **unpinned** baseline AC whose §9 code anchor falls inside the change's
  `files_hint`, emits a `tests`-layer **characterization task** first (a test that pins today's
  behaviour, green on the current code), and makes the change's tasks touching that code depend on it.
- **review** — stage 1 also checks that every baseline AC not marked `supersedes` still holds in
  the touched code (a silent behaviour change is a stage-1 finding).
- **fix** — baselines are ordinary `docs/features/*/spec.md` files, so triage finds them: a
  violated observed AC is a **regression**; a `known-defect` AC is a **spec-bug** (the fix flips
  the AC to the owner's expectation and removes the marker).
