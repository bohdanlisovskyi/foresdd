# Interview depth — easy / medium / hard (the depth dial)

> **Reference-only.** Not a skill. The dial tunes **how much a skill decides on its own vs. asks
> you** — question volume, autonomy, which analyses run, and whether each diagram is confirmed
> per-item or written and ledgered. It does **not** tune *completeness*: every acceptance criterion
> is still covered at every level (see the coverage floor below).
>
> **Who reads it.** *Asking stages* — `specify` · `clarify` · `design` · `ux-flows` — may open with
> the depth question. *Reading stages* — `sequences` · `screens` · the critic resolution flow
> ([`critic.md`](./critic.md)) — use the level, never ask for it. `interview` follows its own
> ceiling rules (§ «Interview exception» at the end) and neither reads nor writes `.depth`.

## The three levels at a glance

| | **easy** | **medium** (default) | **hard** |
|---|---|---|---|
| **In one line** | «Trust the defaults, show me what you assumed.» | «Walk the real decisions with me.» | «Interrogate me, run everything, leave nothing un-probed.» |
| **Typical effort per stage** | Only the un-inferable / irreversible questions (often 0–3) + **one** ledger review. Fastest. | Every real decision, batched ≤4 per round — typically 3–5 questions per stage on an M feature, more on L/XL. | Every decision with its trade-off, adversarial edge probing; on `specify` the full ideation suite (4 agents). Longest. |
| **Pick it when** | Small or easily reversible change; conventions are fine. | Most features. | A mistake is expensive — security, money, data loss, a public contract. |

The dial scales *effort spent asking*, not *effort spent being correct*.

## How the level is resolved (feature stages)

A stage resolves the level once, at the top of its run — highest wins:

1. **`--depth=easy|medium|hard`** on the invocation → silent, **this run only**. If the feature has
   no `.depth` yet, the value is also written there (it becomes the feature's level).
2. **`docs/features/<slug>/.depth`** → silent. Announce it in one line so the user knows it can
   change: «Depth: medium (chosen in specify) — say "deeper" or "faster" at any question to change it.»
3. **The opening question** — only an *asking stage*, only when neither of the above exists. ONE
   depth-selection `AskUserQuestion`, phrased per [`style.md`](./style.md) (explanatory, every term
   glossed). Its «(Recommended)» first option is `interview_depth` from `.claude/sdd.local.md`,
   else **medium** — **except when the feature's `.route` is already `quick`, where `easy` is
   recommended** (the quick-route softening, [`tshirt-sizing.md`](./tshirt-sizing.md)). `specify`
   resolves depth **before** sizing, so on a brand-new feature there is no route yet and the
   softening doesn't apply; at easy, the size + route are then inferred and ledgered, not asked. Each option's description says what the
   level will *do to this run* («easy → I'll decide the reversible calls myself and list them for
   you to veto»; «hard → I'll walk every decision and run the full analysis suite») plus the
   typical-effort cell above; the question ends with the mid-run line («you can say "deeper" /
   "faster" at any later question»). Write the answer to `.depth` **immediately**.

A *reading stage* with no `.depth` uses `interview_depth` (else medium), says so in one line, and
doesn't write the file.

**The net effect: one depth question per feature, not one per stage.** In practice `specify` asks
and every later stage reuses the answer.

### The `.depth` file

- One line — `easy`, `medium` or `hard` — next to `.size` and `.route`. Written by an asking stage's
  opening question, by a `--depth=` run when the file is absent, or by a mid-run change (below).
- Committed in the writing stage's **first** commit (it is a one-line setting, not a document —
  see [`write-and-commit.md`](./write-and-commit.md)).
- To re-choose: say «deeper» / «faster» / a level name during any run, pass `--depth=` for one run,
  or delete `.depth` to be asked again.
- `interview_depth` in settings is only the default for features **without** a `.depth` — changing
  it via [`../config/SKILL.md`](../config/SKILL.md) does not touch features already started. The
  settings file itself (who creates it, the template) is documented in
  [`settings-file.md`](./settings-file.md); a missing file means medium.

## Changing depth mid-run

At any question the user can answer in free text («Other») instead of picking an option:

| User says | Effect |
|---|---|
| «deeper» / «faster» | Shift one level (easy ↔ medium ↔ hard) for the **rest of this run**, rewrite `.depth` so later stages inherit it, and confirm in one line: «Depth → hard for the rest of design and the stages after it.» Then re-ask the pending question at the new level. |
| a level name («switch to easy») | Same, jumping straight to that level. |
| «walk A3» / «walk this one» | Only that ledger item / assumption becomes a real question; the level is unchanged. |

Rules: already-resolved decisions are **not** reopened; ledger entries already recorded stay in
the ledger review; analyses a stage has already passed (e.g. `specify` step 3) are not re-run — a
shift before that step changes what runs. The skill **never shifts on its own**, and the coverage
floor is unaffected. `interview` is excluded — its ceiling changes only on an explicit owner
request (§ «Interview exception»).

## What each level governs (the four axes)

| Axis | **easy** | **medium** (default) | **hard** |
|---|---|---|---|
| **Question volume + autonomy** | Skill decides the reversible / low-stakes calls itself with sensible defaults; asks ONLY the irreversible / high-blast-radius / genuinely-un-inferable ones. **Records every assumption** in the ledger (below) so the user can veto. | The balanced Socratic walk — every real decision asked (batched ≤4 per `AskUserQuestion` call per [`socratic-loop.md`](./socratic-loop.md)), trivial convention-defaults bundled. | Walks **every** decision; each question **foregrounds the trade-off** (what you gain / lose / the hidden catch); probes edge cases harder. |
| **Ideation analyses** (`specify` step 3) | Skip the suite — deep-dive answers only. | `researcher` (competitive/web) + `devils-advocate`. | Full suite: `researcher` + `strategist` (3 approaches) + `analyst` (multi-perspective) + `devils-advocate`, then the Claude-proposed RICE/feasibility confirm. |
| **Diagram confirmation** (`design` C4, `sequences` flows, `ux-flows` flows) | Write the diagram + **one ledger entry** per diagram, then proceed — no per-diagram question (per [`diagram-presentation.md`](./diagram-presentation.md)). | Structured description + `AskUserQuestion` confirm **per diagram**, batched ≤4 per call. | Same as medium — structured description + confirm per diagram (never raw Mermaid). |
| **Edge-case / ambiguity probing** | Only the edges that change the blast radius. | The spec's stated error/authz/edge criteria. | Adversarial — hunt for unstated edges, run the full `devils-advocate` pass, push on every «what if». |

Read the axes together, not in isolation — the «In one line» row above is the summary.

## The assumptions ledger (easy only)

At `easy`, every decision the skill made **for** the user (instead of asking) is recorded as one
ledger entry and reviewed together before the write-point. At medium/hard there is no ledger —
those levels asked directly.

### Entry format

```
- A<n> · <high|low> · <decision> = <chosen value> — because <default rationale>. (<path:line> once written)
```

- **Risk tag.** `high` when the entry shapes an acceptance criterion or other coverage-relevant
  wording, is hard to reverse, or spans several modules/stages; otherwise `low`. (A decision that
  is *both* high-risk and un-inferable is not a ledger entry — easy must ask it.)
- **Numbering.** IDs are assigned at review time in **display order**, so `A1` is always the first
  entry the user sees. The critic's auto-applied fixes keep their own `C<n>` id alongside
  ([`critic.md`](./critic.md) §Depth dial).
- **Order.** `high` entries first, then the rest in document order (section by section).

### The review — one question

Before the write-point, show the ledger and ask ONE `AskUserQuestion`:

- **≤8 entries** — list them all. Options: **Accept all** · **Walk the high-risk ones** (each `high`
  entry becomes a real question) · **Veto by number** (free text: «veto A3, A7», «walk A2»).
- **>8 entries** — **group** the list by section/topic, each group with a header and counts
  («§5 Acceptance criteria — 6 assumptions, 1 high»); `high` entries are listed first inside their
  group and also repeated in a short «High-risk» block at the top. Options: the three above plus
  **Walk a group** (name it — its entries become real questions, batched ≤4 per call).

Make **Walk the high-risk ones** the «(Recommended)» option whenever any `high` entry exists; else
**Accept all**. A vetoed or walked entry becomes a medium-style question for that one item. This is
easy's safety net: autonomy without silent commitment — the user sees every default before it's
locked, ranked so the risky ones can't hide in a long list. Without the native tool, the same
review runs as numbered plain text ([`fallbacks.md`](./fallbacks.md)).

## The coverage floor is depth-independent (correctness, not a preference)

Depth tunes **how many questions** and **how much autonomy** — never **what gets covered**. The completeness guarantees hold at **every** level:

- Every spec §4 user story has ≥1 acceptance criterion (the **use-case floor**); §5 keeps ≥1 AC of each of the 5 coverage types (`specify`).
- Every §4 user story maps to ≥1 flow, and every §5 AC maps to a flow, a branch, or an explicit N/A (`sequences` use-case + AC→flow coverage check).
- Every user story + AC traces end-to-end spec → sequences → data-model → api → tasks → implement (`review`).

`easy` reaches these by **deciding** the «how» with defaults and listing them in the ledger; `hard` reaches them by **asking**. The destination is identical. A skill must never drop an AC, a coverage type, or a flow because the level is `easy` — that's a correctness bug, not a depth choice. If easy can't infer the «how» for a coverage-relevant decision, that decision is one of the «irreversible / un-inferable» ones it **must** ask about regardless of level.

## Per-skill adaptation (the delta each consuming skill applies)

Asking stages:

- **`specify`** — usually the stage that asks and writes `.depth`. The level gates step 3's ideation suite (table above) and the volume of the step-2 deep-dive + step-7 Socratic validation. The §5 coverage gates (≥1 of each of the 5 AC types **and ≥1 AC per §4 user story** — the use-case floor) are **floor, not dial** — enforced at every level.
- **`clarify`** — the level gates how aggressively the self-sweep + `devils-advocate` hunt (easy: only build-divergence that changes behavior, ledgered; hard: adversarial, every fork surfaced) and the per-finding question volume. Every surfaced ambiguity is still Resolved or Deferred at every level — none dangling.
- **`design`** — the level gates the per-section Socratic question volume (easy: decide convention-defaults itself + ledger, ask only blast-radius decisions; hard: walk every decision, foreground each trade-off) and the C4 diagram confirmation (per [`diagram-presentation.md`](./diagram-presentation.md)). The blast-radius → ADR gate and the §11 owner+due rule are floors, enforced at every level.
- **`ux-flows`** — the level gates the per-flow confirmation (diagram axis). When it does ask the depth question, it shares the call with the platform-posture question. Every UI-touching story still gets its flow.

Reading stages:

- **`sequences`** — per-flow confirm (medium/hard) vs. write + ledger entry (easy). Flow coverage is a floor.
- **`screens`** — per-screen confirm (medium/hard) vs. derive + ledger, asking only where the AC↔state mapping is genuinely ambiguous (easy). The full state set is a floor.
- **critic resolution** — at easy, `mechanical` findings auto-apply into the ledger; F1–F4 findings are asked at every level ([`critic.md`](./critic.md)).

A consuming skill adds a one-line pointer to this file at its depth-resolution step and otherwise reads the level as a parameter into its existing loop — it does not re-implement the dial.

## Interview exception

`interview` resolves a **ceiling**, not a mandatory interview length: explicit
`--depth=easy|medium|hard` → saved `interview_depth` → `medium`. It announces the ceiling and
starts from existing context, without a depth-selection question, and it neither reads nor writes
`.depth`. Easy ≤4 substantive user questions; medium ≤10; hard ≤15. Count all questions seeking
user decisions/facts, including identity clarification and final acceptance; reserve room for an
unconfirmed consequential choice. There is no minimum. Reaching a ceiling means summarize actual
readiness and blockers, not invent answers or automatically upgrade the budget. The owner may
explicitly change it.

Risk controls independent critique; a decision-changing factual gap controls research. Neither
is switched on just because the ceiling is hard, nor switched off because it is easy. An
adversarial request triggers critique, not an automatic increase of question count. At every
level, label owner-reported/source-verified/assumption/unknown, and distinguish unconfirmed
recommendations from owner decisions. No decide-for-user easy mode and no assumptions ledger in
`interview`. Its frontmatter `depth` stores the resolved ceiling even when the conversation ends
earlier. Its eight-section brief separates structural completeness from readiness; repo/Plan
Mode/headless write gates apply.

This exception has precedence over every generic rule above for `interview`.
