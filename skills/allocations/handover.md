# Stage handoff — what every skill prints when it finishes (the output contract)

> **Reference-only.** Not a skill. **Every** skill ends by emitting the handoff block defined here —
> as its **last output**, after its structural self-check and its per-document commits
> ([`write-and-commit.md`](./write-and-commit.md)). The format lives only in this file; each
> skill keeps a one-line pointer and supplies its own *What I did* / *Review* / *next command*. This
> exists because a bare «Next: …» line is hard to act on — the user can't tell what changed, which
> files to open, what needs their attention, or what to run next without scrolling back.

## The block (sectioned format)

~~~md
## <status> <skill> — <slug>
<pipeline trail>   ← feature-scoped stages only; see «Pipeline trail»

**What I did**
- <1–3 bullets: the artifact(s) produced/changed>
- size M + route standard (from `.size`/`.route`)
- committed `<sha>` <message>   ← one line per commit, or the reason it was skipped

**⚠ Needs your attention**   ← omit the whole section when empty
- <a deferred question, an override, a defaulted size/route, a skipped commit, a failed check>

**Review before continuing**
- [docs/features/<slug>/<file>](docs/features/<slug>/<file>) — <what to check here>
- [docs/features/<slug>/<file2>](docs/features/<slug>/<file2>) — <…>

**Run next**
1. `/clear` — recommended: the next stage re-reads everything from disk, so a fresh context is cheaper and avoids stale assumptions
2. then run:
   ```
   /foresdd:<next> <slug>
   ```
   ↳ or `/foresdd:<alt> <slug>` to <skip condition>   ← only when a real skip exists
~~~

### Status marker

The heading's first glyph tells the user at a glance how the run ended:

| Marker | Meaning | Use when |
|---|---|---|
| `✅` | complete | every artifact written, self-check passed, nothing in *Needs your attention* |
| `⚠️` | complete with caveats | the stage finished, but *Needs your attention* is non-empty — incl. an unresolved, overridden or degraded self-check item (artifact on disk, maybe uncommitted) |
| `⛔` | blocked | the stage refused, aborted, or stopped before writing its artifact — use the *Blocked* variant |

### Pipeline trail

One line under the heading, for **feature-scoped** stages (`specify` → `ship`, plus `fix`/`decide-adr`/
`tshirt-size`/`glossary` when run for a slug). Omit it for repo-level runs (`survey`, `scaffold`,
`interview`, `roadmap`, `config`, `design-system`).

```
specify ✓ → clarify ✓ → ux-flows ↷ → design ✓ → sequences ▶ → data-model → … → ship   · M / standard
```

- `✓` done (its artifact is on disk), `↷` skipped (fast-lane / N/A), `▶` the stage *Run next* names,
  bare = still ahead. The stage that just ran is the last `✓`.
- Derive it from the artifacts on disk and the resolved `.route`, not from memory. Stages that don't
  apply to this route (e.g. `ux-flows`/`screens` with no UI surface) show as `↷`.
- Collapse the pending tail after the `▶` stage plus one more into `… → ship`, so the line stays short.
- End with `· <size> / <route>` (the same values *What I did* states).

## Rules for filling it

- **Always emit it** as the final output, once per run, after the commits. Never end a
  skill on a bare «Next: X».
- **Headings are fixed English** — `What I did`, `Needs your attention`, `Review before continuing`,
  `Run next` — whatever language the documents or the conversation use. The bullet
  *content* may follow the conversation language; commands and paths never change.
- **What I did** — concrete and self-contained: name the files written and every commit made
  (short SHA + message), or why a commit was skipped (nothing changed, not a git repo, merge in
  progress, `auto_commit: off` → the ready-to-run commands), so the user doesn't scroll up to
  reconstruct it.
- **State the self-check result** — exactly one line in the fixed format of
  [`self-check.md`](./self-check.md) («self-check: 6/6 pass», with `(auto-fixed: …)` /
  `(degraded: …)` suffixes when they apply); a nested skill's result is a second
  `self-check (<inner skill>): …` line. Its details never live here — they go in *Needs your attention*.
- **State the size + route used.** *What I did* names the `feature_size` AND the route the stage
  worked at — «size M + route standard (from `.size`/`.route`)»; a stage that uses the depth dial
  appends it — «· depth medium (from `.depth`)» ([`interview-depth.md`](./interview-depth.md)). A missing `.route` always means
  `standard` (the pre-route behaviour — fully back-compatible). (`specify` establishes both at the
  start, so defaulting should be rare.)
- **Needs your attention** — everything the user must know before moving on, one bullet each,
  phrased as what to do: a §8 question deferred (owner + due), a critic finding overridden, a
  defaulted size/route («size M (default — no `.size`; run `/foresdd:tshirt-size <slug>`)»), a
  commit skipped for a reason other than «nothing changed», a check that was degraded (e.g. `mmdc`
  unavailable → structural lint only), an unresolved self-check item (its label + what's wrong
  + what was tried + the user's choice: re-check / commit anyway / left uncommitted with the
  commands), a self-check override. Not a second *What I did* — routine facts stay there. Any
  bullet here turns the status marker into `⚠️`.
- **Review before continuing** — list **every artifact this stage wrote or changed**, each as a
  **markdown link** whose target is the repo-relative path (`docs/features/<slug>/…`, or a repo-root
  path like `docs/architecture-map.md`) plus a one-liner on what to eyeball. Links are clickable in
  IDE and web hosts; in a plain terminal they still read as the path. This *is* the per-gate review
  checklist — order it most-important first.
- **Run next** — the next command in **`/foresdd:<name> <slug>`** form inside a fenced code block (so the
  user copies it in one click). `/clear` is step 1 and **recommended** for a forward backbone handoff —
  always state it, with the reason, and never fold it into the same code block as the next command
  (the user runs them one after the other). Add a `↳ or …` skip-alternative **only** when one
  genuinely exists (see the table). The skip-alternatives come from the **fast-lane N/A conditions** in
  [`tshirt-sizing.md`](./tshirt-sizing.md); **how each resolves is route-dependent** — auto-skip on
  `quick`, offered on `standard`, suppressed on `full` (see the *Route-resolved forward handoff*
  variant below).
- **Two-step successors** — when the table names a follow-up after the next stage (`tasks` →
  `plan-tests` → `implement`), *Run next* shows only the immediate command; mention the follow-up in
  one trailing line («after that: `/foresdd:implement <slug>`»), never as a second code block.
- Keep the `<slug>` substituted with the real slug — never leave the literal `<slug>` in the printed
  block.

## Variants

- **Backbone forward handoff** (`survey → … → review → ship`): `/clear` recommended + the next stage.
- **Route-resolved forward handoff** (a backbone stage whose successor is an *optional* stage —
  `specify`, `clarify`, `design`, `sequences`, `data-model`, `api`, `tasks`): before printing *Run next*,
  resolve the next stage per `docs/features/<slug>/.route` and the Routes table in
  [`tshirt-sizing.md`](./tshirt-sizing.md):
  - **`quick`** — evaluate the next optional stage's N/A condition yourself. Holds → *Run next*
    names the post-skip stage, *What I did* states «auto-skipped `<stage>`: <reason>», the trail
    marks it `↷`, and the `↳ or` line **inverts** — it offers the skipped stage («run the full
    path»). Doesn't hold → normal forward handoff (the stage is not skipped).
  - **`standard`** — normal forward handoff; add the `↳ or` skip-alternative when the N/A
    condition holds (the user picks).
  - **`full`** — normal forward handoff; **never** print an `↳ or` skip line.
  Missing `.route` → `standard`. The route steers handoffs only — a stage invoked directly always
  runs.
- **Loop-back** (`review → fix | implement` on `CHANGES REQUESTED`): **no `/clear`** — you stay in context
  to iterate; *Run next* = `/foresdd:fix <slug>` for each localized finding and/or `/foresdd:implement <slug>`
  for task-sized ones, then `/foresdd:review <slug>` (it re-runs in delta mode on the changed surface).
  Status `⚠️`; *Needs your attention* lists the findings to fix (or points at the review file).
- **Terminal** (`ship`): there is no `/foresdd:` successor. *Run next* becomes **Done** — the PR
  command/URL + «merging to main is your call»; still print *What I did* + *Review* (the changelog +
  PR). The trail ends `… → ship ✓`.
- **Utility** (`interview`, `config`, `tshirt-size`, `glossary`, `decide-adr`, `roadmap`, `design-system`, `fix`): called ad-hoc, not a
  gate. `/clear` is **optional** (recommend it only if the context is large); *Run next* = «resume
  your backbone stage», naming the likely one (e.g. `/foresdd:design <slug>`) — read it off the trail
  (the first stage not yet `✓`/`↷`). Print *What I did* + *Review* (the one file it wrote). One
  exception: `fix` alone adds a **conditional** recommendation — when the fix touched >5 files or
  crossed a module boundary, *Run next* also offers `/foresdd:review <slug>` (a recommendation, never
  a gate).
- **Blocked** (any skill that hard-refuses on a missing input, hits an unrecoverable error, or is
  stopped by the user before its artifact is written): still emit a block — never end on a bare
  refusal sentence.

  ~~~md
  ## ⛔ <skill> — <slug>
  <pipeline trail>

  **Why I stopped**
  - <the missing input / failed check / user abort, with the real path>

  **What I did**
  - <anything already written or committed — or «nothing written, nothing committed»>

  **Run next**
  ```
  /foresdd:<prerequisite> <slug>
  ```
  ↳ then re-run `/foresdd:<skill> <slug>`
  ~~~

  No `/clear` (the user is likely to fix the blocker in this context). When a partial artifact was
  written to disk, list it under *Review before continuing* so the user knows it exists.

## Canonical sequence (stage → review-files → next)

Paths in this table are relative to `docs/features/<slug>/` unless they start with `docs/`, `.claude/`,
or are repo-root files (`CONTEXT.md`, `CHANGELOG`). Print them in full in the block.

| Stage | Review before continuing (files written) | Run next |
|---|---|---|
| `interview` | `docs/idea-brief.md` (eight sections; conversation artifact when writes are prohibited) | Only `ready-for-roadmap` → `/foresdd:roadmap`; `ready-for-specify` → `/foresdd:specify <slug>`. Otherwise name the evidence action, reframe, or stop. `survey` is suggested separately if a repo map is needed. |
| `survey` | `docs/architecture-map.md` (+ scaffold `tasks.json` on greenfield) | `/foresdd:roadmap` when a brief is on disk (the map supplies the zones) ↳ or brownfield → `/foresdd:specify <slug>`; greenfield → `/foresdd:scaffold` |
| `scaffold` | the materialized skeleton (committed diff) + green smoke test | `/foresdd:specify <slug>` |
| `specify` | `spec.md`, `.size`, `.route` | `/foresdd:clarify <slug>` ↳ or `/foresdd:ux-flows <slug>` (zero §8 OQ — fast lane; no human-facing UI → `/foresdd:design <slug>`) |
| `clarify` | `spec.md` (tightened) (+ `CONTEXT.md` when terms were added) | `/foresdd:glossary <slug>` (optional glossary hop) ↳ or `/foresdd:ux-flows <slug>` (no human-facing UI → `/foresdd:design <slug>`) |
| `ux-flows` | `ux-flows.md` (flows + SCR inventory) | `/foresdd:design <slug>` |
| `design` | `sad.md` (C4 §3/§5 + `target_surfaces`) + `adr/` | `/foresdd:sequences <slug>` ↳ or `/foresdd:data-model <slug>` (XS/S, no multi-step flow — fast lane) |
| `sequences` | `sad.md` §6 (flows) | `/foresdd:data-model <slug>` ↳ or `/foresdd:api <slug>` (XS/S, no schema change — fast lane) |
| `data-model` | `data-model.md` + staged `migrations/` | `/foresdd:api <slug>` ↳ or `/foresdd:screens <slug>` (XS/S, no contract change — fast lane; no UI surface → `/foresdd:tasks <slug>`) |
| `api` | `contracts/openapi.yaml` (+ `events.md`, `api-sync-report.md`) | `/foresdd:screens <slug>` ↳ or `/foresdd:tasks <slug>` (no UI surface in `target_surfaces` — fast lane) |
| `screens` | `screens.md` (+ `screens.pen` / Figma node-refs per tool) | `/foresdd:tasks <slug>` |
| `tasks` | `tasks/` + `tasks.json` | `/foresdd:plan-tests <slug>` — after that: `/foresdd:implement <slug>` (two-step successor) |
| `plan-tests` | `test-plan.md` (or `spec.md` `## Test plan` for XS/S) | `/foresdd:implement <slug>` |
| `implement` | the committed diff (code + tests) + `tasks/tracker.md` / `tasks.json` statuses (+ `docs/roadmap.md` `Status: building`) | `/foresdd:review <slug>` |
| `review` | `_review/review-<date>.md` (committed; + `spec.md` when a finding was deferred) | `/foresdd:ship <slug>` (PASS) · `/foresdd:fix <slug>` per localized finding / `/foresdd:implement <slug>` per task-sized one, then `/foresdd:review <slug>` (delta) (CHANGES, no `/clear`) |
| `ship` | `docs/features/<slug>/changelog.md` (+ the root `CHANGELOG.md` entry when that file exists) + `docs/roadmap.md` (each committed before the PR) + the PR | **Done** — PR URL (or the command); merge is your call |
| `config` | `.claude/sdd.local.md` (the settings file itself is gitignored — the `.gitignore` patch is the only thing to commit) | resume your backbone stage — e.g. `/foresdd:specify <slug>` |
| `tshirt-size` | `.size` + `.route` | resume — e.g. `/foresdd:specify <slug>` |
| `design-system` | `docs/design-system.md` | resume — e.g. `/foresdd:ux-flows <slug>` |
| `glossary` | `CONTEXT.md` (repo root or per-feature) | resume — e.g. `/foresdd:design <slug>` |
| `decide-adr` | `adr/NNNN-<title>.md` | resume — `/foresdd:tasks <slug>` or `/foresdd:plan-tests <slug>` |
| `roadmap` | `docs/roadmap.md` | resume your backbone stage |
| `fix` | `_fixes/<date>-<short>.md` + the diff (+ the spec patch if any) | resume — or `/foresdd:review <slug>` when the fix was wide (>5 files / cross-module) |

The `↳ or` cells above show the `standard`-route rendering; on `quick` the stage auto-skips (and
the `↳ or` inverts), on `full` the `↳ or` line is dropped — per the *Route-resolved* variant.

## Example (rendered)

~~~md
## ⚠️ design — rate-limit-bump
specify ✓ → clarify ✓ → ux-flows ↷ → design ✓ → sequences ▶ → data-model → … → ship   · M / standard

**What I did**
- Wrote the SAD (§1–§12, C4 L1/L2) and 2 ADRs; `target_surfaces: [api]`
- size M + route standard (from `.size`/`.route`)
- committed `a1b2c3d` design: rate-limit-bump ADR-0001 use-token-bucket
- committed `d4e5f6a` design: rate-limit-bump ADR-0002 per-tenant-limits
- committed `9f8e7d6` design: rate-limit-bump sad.md

**⚠ Needs your attention**
- Critic finding on §8 overridden by you — rationale recorded in §1 ¶4
- `mmdc` not installed → Mermaid checked by structural lint only

**Review before continuing**
- [docs/features/rate-limit-bump/sad.md](docs/features/rate-limit-bump/sad.md) — §5 building blocks and §9 decisions
- [docs/features/rate-limit-bump/adr/0001-use-token-bucket.md](docs/features/rate-limit-bump/adr/0001-use-token-bucket.md) — consequences are honest

**Run next**
1. `/clear` — recommended: the next stage re-reads everything from disk
2. then run:
   ```
   /foresdd:sequences rate-limit-bump
   ```
   ↳ or `/foresdd:data-model rate-limit-bump` to skip sequences (XS/S, no multi-step flow)
~~~

## Discipline

- **The block is the last thing printed — every run, no exceptions** (a refusal or abort included —
  that's the *Blocked* variant). A skill that ends on prose without it has regressed.
- **Status is honest.** `✅` only when *Needs your attention* is empty; never print `✅` over a
  deferral, override, defaulted size/route or degraded check.
- **Real paths, not descriptions.** «the SAD» is not reviewable;
  [docs/features/<slug>/sad.md](docs/features/<slug>/sad.md) is.
- **The next command is copy-ready** — `/foresdd:<name> <slug>` alone in a fenced block, slug
  substituted.
- **`/clear` only where it's useful** — recommended on a forward backbone handoff, omitted on a
  loop-back or a blocked run (you're iterating), optional after a utility.
- **Format canonical here** — a skill that hand-rolls its own block shape has duplicated the contract.

## Where each skill calls this

Every skill's final protocol step ends with: «emit the **stage-handoff block** per
[`handover.md`](./handover.md)» + its own next command from the table above. The format + variants live
here; the skill supplies only the run-specific content.
