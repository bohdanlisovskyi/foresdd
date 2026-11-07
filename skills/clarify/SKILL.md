---
name: clarify
model: inherit
effort: high
agents: [devils-advocate]
description: >
  Use to run an ambiguity sweep over a written spec.md and close every under-specified point
  before planning or design proceeds — so two engineers can't reasonably build different things
  from the same spec. Triggers on "clarify {slug}", "find ambiguities in {slug}", "is the spec
  ready", "sharpen the spec", "/foresdd:clarify {slug}". Re-reads the spec, dispatches a clean-context
  devil's-advocate subagent to list where the spec forks, shows all findings in one overview, then
  resolves them in batches with AskUserQuestion — RESOLVE (tighten §1/§5/§6 in place) or DEFER
  (→ §8 Open questions with owner+due). Output: an updated docs/features/{slug}/spec.md with every
  ambiguity resolved or deferred — none dangling. Hard-refuse if spec.md is missing.
---

# Skill: clarify

Ambiguity sweep over a written `spec.md`. It hunts the spec for under-specified points — vague terms, unmeasured NFRs, AC missing error/authz/edge behavior, unstated assumptions, conflicting requirements, undefined domain terms, missing actors, scope creep — then dispatches a **clean-context devil's-advocate subagent** that re-reads the spec fresh and answers one question: *where would two engineers reasonably build different things from this?* Each ambiguity it surfaces is closed with the user: either **resolved** (the spec is tightened in place) or **deferred** (a §8 Open-Questions row with owner + due). It exists so the downstream stages (`ux-flows`, `design`, …) never proceed on an ambiguous spec.

This is a sweep, not a full authoring stage — it does **not** run the shared Socratic loop or the coherence critic. Its shared dependencies:
→ [`../allocations/critic.md`](../allocations/critic.md) (clean-context **dispatch discipline** only — the subagent here hunts AMBIGUITY, not coherence drift) · [`../allocations/style.md`](../allocations/style.md) (resolve/defer question phrasing).

Depth governs how aggressively the sweep hunts + the per-finding question volume → [`../allocations/interview-depth.md`](../allocations/interview-depth.md). (Every surfaced ambiguity is still Resolved or Deferred at every level — that's a floor, not a dial.)

## Owner

PM + Tech Lead (the spec's co-authors resolve their own ambiguities). PM owns vague-term / scope / missing-actor calls; Tech Lead owns unmeasured-NFR / under-specified-AC / conflicting-requirement calls. These owners are also the **pre-filled default owner** of a deferred finding of that class.

## Inputs

- `<slug>` — same feature slug used by `specify`.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/spec.md`. Absent → STOP and emit the *Blocked* handoff ([`../allocations/handover.md`](../allocations/handover.md)) pointing at `/foresdd:specify <slug>` — clarify sharpens an existing spec, it does not write one.
- (Optional) `CONTEXT.md` — two-level: read **both** repo-root (project-wide) and `docs/features/<slug>/CONTEXT.md` (feature-scoped; wins on conflict) → [`../glossary/SKILL.md`](../glossary/SKILL.md); if present, `## Glossary` is canonical; an "undefined-term" finding for a word already glossed at either level is a false positive (drop it).
- **Fast lane (XS/S):** when `specify` produced zero §8 open questions and flagged no ambiguous AC, the skip of this stage is offered by **`specify`'s handoff** (→ the fast lane in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md)) — the user takes it there; clarify itself never auto-skips.

## The run at a glance — progress

Five phases, numbered as the protocol steps below:

```
1 Gate & depth → 2 Hunt (devil's advocate ∥ self-sweep) → 3 Overview → 4 Resolve → 5 Wrap-up & commit
```

- **Phase banner** at the start of every phase: `▸ clarify <n>/5 · <phase> — next: <next phase>`.
- **Finding marker** on every resolve question: the question text starts with `clarify 4/5 Resolve · finding <k>/<N> · <class> · <§ref>`; the `header` chip carries `<k>/<N>` (follow-ups: `<k>/<N> · follow-up`).
- **Waiting is announced** — step 2 says the subagent is running and roughly how long, and that no input is needed.
- **Mini-recap every ~5 findings** — one line: `resolved 3 · deferred 1 · dropped 1 · 6 to go`.

## Protocol

1. **Gate + set interview depth.** `test -f docs/features/<slug>/spec.md` → missing = refuse with the *Blocked* handoff above. Read the spec (and `## Glossary` from both root `CONTEXT.md` and `docs/features/<slug>/CONTEXT.md` if present — per-feature wins — to suppress false "undefined-term" hits). **Then set the interview depth** per the resolution order in [`../allocations/interview-depth.md`](../allocations/interview-depth.md): `--depth=` (this run) → `docs/features/<slug>/.depth` (reuse, one-line announce — the normal case after `specify`) → otherwise ONE depth-selection `AskUserQuestion` phrased per [`../allocations/style.md`](../allocations/style.md), with `interview_depth` from `.claude/sdd.local.md` (else medium) as the «(Recommended)» first option, the answer written to `.depth`. The level tunes how adversarially the sweep + subagent hunt (easy: only build-divergence that changes behavior, with assumptions stated; medium: balanced; hard: adversarial, every fork surfaced) and the per-finding question volume → [`../allocations/interview-depth.md`](../allocations/interview-depth.md).
2. **Hunt — devil's advocate in parallel with the self-sweep.**
   - **Dispatch first (the core mechanic).** Dispatch the [`devils-advocate`](../../agents/devils-advocate.md) agent — `subagent_type: "foresdd:devils-advocate"` (model per `judgment_model`, roster default `opus`; effort `high`; clean context — it never saw this conversation) — **in the background**, then tell the user: «Devil's advocate is re-reading the spec from scratch (it hasn't seen our conversation) — usually a minute or two; nothing needed from you.» Pass only the slug + the spec path; it Reads `spec.md` (and `CONTEXT.md`) itself — inline nothing — and returns "two engineers would diverge here" findings. The dispatch follows the contract in [`../allocations/agent-roster.md`](../allocations/agent-roster.md) (clean-isolated context, cited findings, `NO_AMBIGUITIES` if none). If `devils-advocate` is unavailable at runtime, fall back to a `general-purpose` Agent with the prompt body in [`./references/ambiguity-checks.md`](./references/ambiguity-checks.md).
   - **Self-sweep while it runs.** Walk the spec against the eight ambiguity classes in [`./references/ambiguity-checks.md`](./references/ambiguity-checks.md) (vague-term / unmeasured-NFR / under-specified-AC / unstated-assumption / conflicting-requirement / undefined-term / missing-actor / scope-creep). Note candidate findings with a `§ref` each — do not edit yet. Treat each `high` entry in §8.1 Assumptions as a candidate `unstated-assumption` check: is it still true, and does an AC silently depend on it?
3. **Overview — merge, dedupe, show the whole list once.** Union the self-sweep with the subagent findings; collapse duplicates (same `§ref` + same class). Order highest-impact first (conflicting-requirement > under-specified-AC > unmeasured-NFR > undefined-term > missing-actor > scope-creep > vague-term > unstated-assumption). Then print **one overview table** before any question, so the user sees the size of the job:

   ```
   7 ambiguities found (devil's advocate 5 · self-sweep 4 · 2 overlapped) — I'll ask in 3 rounds.
   | # | Class | Where | Divergence (two builds) | Proposed |
   |---|---|---|---|---|
   | 1 | conflicting-requirement | §2 vs §6 | real-time vs nightly batch | ask which wins |
   | 2 | under-specified-AC | AC-04 | expired invite: block vs auto-renew | add error AC |
   ```

   At `easy`, mark which rows the skill will auto-resolve into the ledger («auto») and which it will ask. **Empty merged set** → report «spec is unambiguous — no two reasonable builds diverge», change nothing, and go straight to step 5's handoff (status `✅`, no commit needed).
4. **Resolve or defer — batched, every option concrete.** Group findings into `AskUserQuestion` calls of **≤4**, in overview order, each phrased per [`../allocations/style.md`](../allocations/style.md) with the finding marker. Ask a finding **alone** when it is a `conflicting-requirement`, or when its resolution changes another finding's options. Options per finding (≤4; «Other» is the 5th):
   - **Apply the proposed tightening** «(Recommended)» when the fix is clear — the description quotes the exact before → after text and the section it lands in, so approving it needs no follow-up.
   - **Defer to §8 — owner <X>, due <Y>** — pre-filled: owner from the class's owner (§Owner) or the devil's advocate's candidate owner, due = the next stage that would be blocked (e.g. `before foresdd:design`). One click writes a complete row; a different owner/due goes through «Other».
   - **Not an ambiguity** — false positive (e.g. the term is in CONTEXT, the number is already present); dropped, no edit.
   - For a `conflicting-requirement`: replace the first option with **Keep <A>** and **Keep <B>** (each quoting the line it keeps and the one it rewrites).
   - **«Other»** = the user dictates their own tightening, or a different owner/due for the defer.

   Every finding ends Resolved or Deferred (or dropped as not-an-ambiguity) — none dangling. A Defer typed without owner or due → re-ask once with the pre-filled values as «(Recommended)»; still missing → the finding stays unresolved and is named in *Needs your attention*. Each answer is written to `spec.md` **immediately**, before the next batch. **Depth tunes the question volume, not the floor:** at `easy`, the skill resolves the unambiguous, low-stakes findings itself with sensible tightenings and records them in the assumptions ledger, asking only the behavioral/high-stakes forks; at `hard`, it asks every finding. The «zero dangling» rule holds at every level.
   - **Write each resolution back the moment it lands** (not batched at the end → [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md)). Apply a Resolve edit in the spec's native section (tighten the §5 AC into business-observable form, replace a §6 adjective with a numeric target + measurement, fix a §1 term, add a missing §4 actor/US, cut a §3 scope-creep line). Append a Defer as a §8 checkbox row `- [ ] <question>? Default now: <X>. — owner: <name/role>, due: <date or stage>` (replacing a `None.` placeholder). Keep a short edits-log (one line per finding: `class · §ref · resolved|deferred|dropped · before→after`).
   - **Undefined-term findings reconcile the glossary in-flow (a hard rule, at every depth).** When an `undefined-term` finding is Resolved, immediately invoke `glossary <slug>` for that term — compare it against `CONTEXT.md` and add/update the definition **now**, not as a deferred note. clarify never resolves a term by inventing a meaning inline; the canonical definition lands in `CONTEXT.md` so `design`/downstream read one source.
5. **Wrap-up — summary, stamp, self-check, commit, handoff.**
   - **Ledger review (easy only).** One review of every auto-resolved finding, per [`../allocations/interview-depth.md`](../allocations/interview-depth.md) §The assumptions ledger. A vetoed entry is reverted on disk and asked as a normal finding; accepted entries that encode an assumption (rather than a plain wording fix) are appended to §8.1 Assumptions with their A-id.
   - **Pass summary** (a recap, not a question): counts `resolved · deferred · dropped` per class, every §8 row added (headline + owner + due), and every term added to `CONTEXT.md`.
   - **Stamp + self-check.** Set `updated_at: <today>` in the frontmatter. Re-read `spec.md` from disk and confirm `specify`'s invariants held through the tightening (§5 AC stays free of HTTP/status/error-code/SQL tokens; §6 numbers carry a measurement; §4 roles only from the glossary; every retained US still has ≥1 AC) and zero findings dangle.
   - **Commit per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md)**, one commit per changed document: `clarify: <slug> spec.md (N resolved, M deferred)`, `clarify: <slug> CONTEXT.md` for each glossary file the in-flow `glossary` calls changed — an unchanged file is skipped.
   - **Emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) — *What I did* (the pass-summary counts, incl. the terms already reconciled into `CONTEXT.md` by the in-flow `glossary` calls — the user learns here that the glossary changed, not later) + *Needs your attention* (each deferred question with owner + due; any finding left unresolved) + *Review* (tightened `spec.md` — name the sections that changed; + `CONTEXT.md` when terms were added) + *Run next* — **resolve the next stage per `.route`** (Routes in [`../allocations/tshirt-sizing.md`](../allocations/tshirt-sizing.md)): forward `/foresdd:glossary <slug>` ↳ or the next backbone stage to skip the glossary hop — that stage is `/foresdd:ux-flows <slug>`, unless `ux-flows`' N/A condition holds (**no human-facing UI** — every §4 actor a system/service, or the repo has no UI at all, per the tshirt-sizing fast lane), in which case it's `/foresdd:design <slug>` (on `quick` — terms were already reconciled in-flow, so auto-resolve straight to that backbone stage unless unglossed terms remain; on `full` — keep both options, no auto-resolve). The same handoff runs when step 3 found nothing.

## Definition of Done

- Every ambiguity from the self-sweep + the subagent is **Resolved** (spec tightened in its native section), **Deferred** (a §8 row with both owner AND due), or dropped as **Not an ambiguity** by the user — zero dangling.
- The overview table was shown before the first resolve question; every resolve question carried its `finding k/N` marker.
- Resolve edits preserve `specify`'s contracts: §5 AC carry no HTTP/status/error-code/SQL tokens, §6 NFR rows carry a numeric target + measurement (no adjectives), §4 roles match the CONTEXT glossary, every retained US keeps ≥1 AC.
- The devil's-advocate subagent actually ran (clean context, Read the spec itself) — not skipped, not paraphrased into the main thread.
- `updated_at` reflects today; edits-log kept; each resolution written to `spec.md` as it landed; after the self-check, `spec.md` and any changed `CONTEXT.md` committed one commit each (SHAs in the handoff).
- The devil's-advocate sweep + the zero-dangling resolution rule are this skill's **structural self-check** ([`../allocations/self-check.md`](../allocations/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **Skipping the subagent** and sweeping only in-thread. The clean-context fork-finder is the core mechanic — the self-sweep is shaped by the conversation that wrote the spec and misses its own blind spots.
- **Asking blind.** Starting the first resolve question before the user has seen the overview — they can't judge how much is left or which findings matter most.
- **Vague options.** «Resolve now» with no proposed text forces a follow-up round per finding; propose the concrete before → after, and pre-fill the defer's owner + due.
- **Resolving an ambiguity unilaterally** (no `AskUserQuestion`). clarify proposes; the author decides — the same user-in-the-loop contract as every SDD stage. (At easy, the ledger review *is* the decision.)
- **Defer without owner+due** — a §8 row missing either is not a real defer; re-ask once, else it stays unresolved.
- **Re-running the coherence critic here.** That F1–F6 cross-section drift check belongs to `specify`/`design`; clarify's subagent hunts *ambiguity* (build-divergence), a different target.
- **Leaking implementation into a Resolve edit** — tightening a §5 AC by adding a status code / endpoint / SQL detail. Stay business-observable; the technical mapping lives in `api` / `data-model`.
- **Inventing answers to fill findings.** A genuinely open point is *deferred* with an owner, not guessed — better an honest §8 row than a fabricated AC.
- **Authoring new scope.** clarify sharpens what the spec already says; a brand-new requirement goes back through `specify`, not in under cover of a "clarification".

## References & template

- [`./references/ambiguity-checks.md`](./references/ambiguity-checks.md) — the eight ambiguity classes (how to spot / how to resolve each) + the clean-context devil's-advocate subagent prompt body.
- [`../allocations/style.md`](../allocations/style.md) — phrasing for the resolve/defer/false-positive question.
- [`../allocations/critic.md`](../allocations/critic.md) — clean-context dispatch discipline reused by step 2 (Reads upstream itself, cited findings, `NO_*` sentinel on empty).
- [`../allocations/interview-depth.md`](../allocations/interview-depth.md) — the easy/medium/hard dial set in step 1 (sweep aggressiveness + per-finding question volume).
