# Clean-context critic — canonical dispatch, F1–F6 skeleton, resolution UX

> **Reference-only.** Not a skill. Skills that run a post-Socratic critic (`specify`, `design`)
> read this file for the canonical dispatch, the failure-class prompt skeleton and the
> resolution flow, and keep only a short **delta** naming their artifact, upstream files, F5
> floor and F6 specialization. `clarify` reuses only the **dispatch discipline** (clean context,
> Reads upstream itself, cited findings, sentinel on empty) for its ambiguity hunt.

## Why a separate critic

The Socratic loop ([socratic-loop.md](./socratic-loop.md)) walks one section at a time and never returns to a written section. So it **cannot** see cross-section drift introduced by later edits, nor structural gaps the author missed while self-editing. The critic is a single **clean-context** agent — it never saw the conversation. It re-reads the draft and the upstream artifacts from disk itself (no paraphrase poisoning) and probes the draft against the edits-log.

## Dispatch (skill side)

1. **Read** this file + the consuming skill's critic delta.
2. **Tell the user it's running** — one line, before the call, so a slow judgment run doesn't look like a hang:
   `Running a clean-context critic over <artifact> — it re-reads everything from disk; this can take a minute or two.`
3. **Fill the placeholders** (table below) and pass the assembled prompt. The prompt is **self-contained** — a fallback agent that never read `agents/critic.md` must be able to run it as is.
4. **Spawn** `subagent_type: "foresdd:critic"` — model per `judgment_model`, effort per [`agent-roster.md`](./agent-roster.md) (`xhigh` on L/XL). Unavailable → the same prompt on `general-purpose` → last resort, run it **inline** per [`fallbacks.md`](./fallbacks.md) and say in the handoff that the critic was not clean-context.
5. **Async hosts** (background/teammate mode): append the report-delivery instruction from [`agent-roster.md`](./agent-roster.md) (shared-contract point 2). An idle/completion signal without content is **not** `NO_CONTESTED_DECISIONS` — pull the full report through the host's messaging channel first.
6. **Handle the result** → [Outcomes](#outcomes), then [Resolution](#resolution).

| Placeholder | Filled with | Required |
|---|---|---|
| `{{ARTIFACT_NAME}}` | e.g. "Software Architecture Document (Arc42 12 sections)" | yes |
| `{{DRAFT_PATH}}` | path of the artifact **on disk** (it was written section by section) — never inline the body | yes |
| `{{EDITS_LOG}}` | the Socratic edits-log, verbatim, schema per [socratic-loop.md](./socratic-loop.md#edits-log-mandatory) | yes (may be empty) |
| `{{UPSTREAM_FILES}}` | bullet list of paths the critic Reads itself — **always include `docs/features/<slug>/.size`** (F2 needs the declared class) | yes |
| `{{F5_FLOOR}}` | the delta's structural-floor checklist | yes |
| `{{F6_RULES}}` | the delta's leak rules | yes |
| `{{EXTRA_PROBES}}` | the delta's F1 specialization + any extra check (e.g. specify's brief preservation) | optional → `none` |
| `{{EXTRA_INPUTS}}` | side logs the delta inlines (e.g. design's ADR-spawns log, specify's owner corrections) | optional → `none` |
| `{{RECHECK}}` | on the re-check run only: the resolved finding list (see [Re-check](#re-check)) | optional → `none` |

## Prompt skeleton (everything below the line is the agent prompt)

---

You are a clean-context critic for a **{{ARTIFACT_NAME}}** draft. You did not see the conversation that produced it. Your job is to detect cross-section drift, coherence damage from user edits, structural gaps, and constraint/quality leaks that per-section Socratic validation could not see. You do **not** propose new ideas — coherence, not vision.

### Inputs

**Draft — Read it yourself:** `{{DRAFT_PATH}}`

**Edits-log** — every `Edit` / `Drop` / `Save as Open Question` the user applied, chronological. `Approve` entries are intentionally absent (baseline). For `save_as_oq`, `after` is the Open-Questions row incl. owner+due. Entries with `decision_id: CRIT-*` are resolutions of an earlier critic run:
```
{{EDITS_LOG}}
```

**Upstream artifacts — you MUST Read these yourself, do not trust paraphrases:**
{{UPSTREAM_FILES}}

**Extra inputs:** {{EXTRA_INPUTS}}

**Re-check context:** {{RECHECK}}

### Method

Read the draft and the upstream files first. Then probe the draft against the edits-log along the six failure classes. Be skeptical: a decision passing Socratic does not mean it coheres with other sections after the surrounding edits. Re-read the cited lines before asserting a contradiction — a critic that invents drift is worse than none.

### Failure classes (probe each)

- **F1 — Vector / recommendation drift.** A choice the upstream artifact committed to (chosen approach, dominant quality goal, recommended option) is silently contradicted by a later section of the draft. Cite the upstream commitment + the contradicting draft line.
- **F2 — Size-class creep.** `edit`/`add` resolutions introduced new modules / object types / branches that push the feature past the class declared in `.size`. Flag even if the user did not see the size implication. If `.size` is absent, skip F2 and say so in one line.
- **F3 — Defer vs upstream vector.** For every `drop` / `save_as_oq`, check whether the upstream artifact named that item a critical driver (engagement / availability / performance / adoption / risk). If yes, the defer re-introduces a vector the team judged too important to drop. **Differentiate**: «dropped» (hard removal, gone from the draft) vs «deferred to Open-Questions» (still alive with owner+due, recoverable if the OQ resolves before downstream stages).
- **F4 — Silent edits.** For every `edit` in the log, the draft text must match the `after` field. Text differing from both `before` and `after` with no log entry = the author silently re-edited after approval, bypassing the Socratic contract.
- **F5 — Coverage / structural regression.** After applying all drops + OQ-migrations, the draft must still meet this floor (OQ-migrated items do NOT count toward coverage):
  {{F5_FLOOR}}
- **F6 — Constraint / quality leak.** Artifact-specific:
  {{F6_RULES}}
- **Extra probes:** {{EXTRA_PROBES}}

### Severity and fix-type

Tag every finding:

- **Severity** — `blocking`: a downstream stage would build the wrong thing, or the artifact fails its floor · `should`: coherence is weakened but downstream still lands correctly · `nit`: cosmetic. Defaults: F4, F1 → `blocking`; F3, F2 → `should`; F5 → `blocking` for a missing required section/diagram, else `should`; F6 → `should`. Override a default only with a one-clause reason.
- **Fix-type** — `revert` (restore the edits-log `after`/`before` text) · `amend` (rewrite a draft line to match upstream) · `fill` (add missing content) · `mechanical` (a deterministic substitution with **no** product or design choice — e.g. replacing a forbidden token, adding an `<!-- N/A: reason -->` note whose reason the draft already states).

### Output format

If 0 findings, output literally `NO_CONTESTED_DECISIONS`. Otherwise one bullet per finding, numbered `C1, C2, …` in priority order:

```
- **[C{n} · {severity} · F{k}] {one-line headline}** — where: {draft §/line}; caused by: {edits-log decision_id | "—"}; contradicts: {upstream path §/line}; fix: {fix-type} — {concrete action}; before: "{verbatim draft snippet}"; after: "{proposed text | —}".
```

- **Judgment findings (F1–F4): at most 7**, highest-impact first (F4 > F1 > F3 > F2).
- **F5/F6 hits do not count toward the cap — list every one.** Group them as **one finding per class per section**, with one sub-bullet per hit (`  - {line ref}: "{snippet}" → "{replacement}"`), so a batch fix stays one decision for the user.
- ≤300 words, excluding the F5/F6 hit sub-bullets.
- **Cite-mode is required**: every finding cites at least one draft location AND at least one upstream location. An uncited finding is invalid — drop it rather than ship it.

### Discipline

- Do NOT propose additions or re-scoping the user did not ask for.
- Do NOT challenge `Approve`-d decisions unless a logged `Edit`/`Drop`/`Save as OQ` or a later section makes them incoherent.
- On a re-check, do NOT re-raise a finding listed as overridden in the re-check context.
- No preamble, no restatement, no closing summary. Bullets only (or a sentinel).
- If you cannot Read the draft or a required upstream file, output literally `CRITIC_BLOCKED: <path> — <reason>` and stop. Do not guess.

---

## Per-skill delta (what each consuming skill supplies)

- **`{{ARTIFACT_NAME}}`** — e.g. "Software Architecture Document (Arc42 12 sections)" or "Product spec".
- **`{{UPSTREAM_FILES}}`** — the files the critic must Read (e.g. spec → `CONTEXT.md`, idea source; design → `spec.md`, `CONTEXT.md`, `adr/`), **plus `.size`**.
- **`{{F5_FLOOR}}`** — the concrete checklist for this artifact (required sections/diagrams/tables).
- **`{{F6_RULES}}`** — the artifact's leak rules. `specify`: forbidden implementation tokens in AC (HTTP verbs, URL paths, status codes, error-code strings, SQL constructs). `design`: NFR-number leak + strawman-ADR + constraint-vs-repo contradiction.
- **`{{EXTRA_PROBES}}` / `{{EXTRA_INPUTS}}`** — F1 specialization, brief-preservation check, ADR-spawns log, owner corrections.
- **Override slot** — where an override bullet lands (`spec.md` / `sad.md`: §1 ¶4).

## Outcomes

Handle the critic's return **before** asking the user anything:

| Return | What the skill does |
|---|---|
| `NO_CONTESTED_DECISIONS` | Say one line — `Critic: no coherence issues found in <artifact>.` — record `critic 0 open`, continue. |
| Findings | Drop any finding that lacks a draft **and** an upstream citation (count them; mention "N uncited findings discarded" in the summary). Continue to [Resolution](#resolution). |
| `CRITIC_BLOCKED: <path> — <reason>` | Wrong/missing path the skill supplied → fix it and re-dispatch **once**, silently. Otherwise (or still blocked) → ask the user: **Retry** / **Continue without the critic** (self-check reports `⚠️ critic skipped: <reason>` in the handoff) / **Stop here** (the artifact stays on disk, uncommitted). |
| Empty, idle-only or malformed (no sentinel, no parseable bullet) | Async: pull the report via messaging. Still nothing → re-dispatch once. Still nothing → treat as `CRITIC_BLOCKED: — no report returned`. |

Never treat a missing report as a clean pass.

## Resolution

### 1. Summary first

Before any question, show one compact table of **every** finding, `blocking` first, so the user sees the whole picture and how much is left:

```
Critic: 5 findings — 2 blocking · 2 should · 1 nit

| ID | Severity | Class | Headline                           | Where | Fix        |
|----|----------|-------|------------------------------------|-------|------------|
| C1 | blocking | F4    | §5 AC-03 differs from approved text | §5    | revert     |
| C2 | blocking | F1    | §6 flow is sync, §4 chose async     | §6    | amend      |
| C3 | should   | F3    | Deferred item was a key driver      | §8    | amend      |
| C4 | should   | F6    | 3 forbidden tokens in AC            | §5    | mechanical |
| C5 | nit      | F5    | §7 empty, no N/A note               | §7    | mechanical |
```

### 2. Depth dial

Read the interview depth ([interview-depth.md](./interview-depth.md)):

- **`easy`** — apply every `mechanical` finding **without asking**: write it to disk, append it to the edits-log (`CRIT-C{n}`) and to the assumptions ledger, and mark it `auto-applied` in the summary table. The user can undo one in free text («undo C4»). Every F1–F4 finding is still asked.
- **`medium` / `hard`** — ask about every finding.

### 3. Batched questions

Ask in `AskUserQuestion` calls of **up to 4 questions**, `blocking` first, then `should`, then `nit`. Phrase per [style.md](./style.md) (label = the next mechanical step, description = what happens + the trade-off). Each question:

- First line of the text: `Critic · C{n} ({severity}) · {k}/{total}` — header chip `C{n} · F{k}`.
- Plain language: what is inconsistent, why it matters downstream — not the raw bullet.
- A **`preview`** with the `before` / `after` text whenever the fix changes the artifact, so the user sees exactly what will be written.

Options by fix-type (first = the critic's suggestion, marked «(Recommended)»):

| Finding | Options |
|---|---|
| F4 silent edit | **Restore approved text** · **Keep current text** (logged as a new edit; asks the reason) · **Override** |
| F1 / F3 drift | **Amend {section} to match {upstream}** · **Move to Open Questions** (asks owner + due) · **Override** |
| F2 size creep | **Trim back to {size}** (revert the creeping edit) · **Re-classify the size** (run the `tshirt-size` protocol) · **Override** |
| F5 gap | **Fill it** (preview shows the proposed content) · **Mark N/A** (asks the reason) · **Move to Open Questions** |
| F6 leak | **Apply the rewrite** · **Override** |
| Grouped `mechanical` hits | **Apply all {N} fixes** · **Review one by one** · **Override all** |

- **Override** asks for a rationale (re-prompt once if empty) and writes, in the delta's override slot: `Decision override: <headline> — <rationale, verbatim> (critic C{n}, F{k})` — so downstream skills see the deliberate choice.
- **Apply each accepted change to disk immediately** and append it to the edits-log as `decision_id: CRIT-C{n}` (action `edit` / `drop` / `save_as_oq`).
- Never resolve a finding without the user, except `mechanical` ones at `easy`.

### 4. Re-check

Re-dispatch the critic **once** when the accepted resolutions changed **2+ sections** or resolved **any F1/F3** finding — a fix in one section can break another. Fill `{{RECHECK}}` with the resolved list (`C{n} · F{k} · {amended | reverted | overridden | auto-applied}`); the critic must not re-raise overridden ones. Resolve new findings the same way. **Never a third run** — anything still open after the re-check is resolved by the user or overridden. Tell the user before the re-check: `Re-checking once — your fixes touched {n} sections.`

### 5. Close

Report the result as this skill's self-check ([self-check.md](./self-check.md)) — `critic 0 open` — and one line in the handoff's *What I did*: `Critic: {found} findings — {amended} amended · {reverted} reverted · {overridden} overridden · {auto} auto-applied{ · re-checked}`.
