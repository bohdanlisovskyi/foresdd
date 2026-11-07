# Draft generation — per-section contract for specify step 5

The authoritative format for each section is the `<!-- instruction -->` comment in [`../templates/spec.md`](../templates/spec.md). This file is the operational glue: where content comes from and what is forbidden.

## Inputs in priority order

1. **`CONTEXT.md` `## Glossary`** — canonical for role names + domain terms. If anything contradicts it, the glossary wins.
2. **The interview** — accepted decisions and relevant evidence from `docs/idea-brief.md`, plus current owner corrections and step-2 specification gaps, per [`brief-reuse.md`](./brief-reuse.md). Reuse the problem, trigger, outcome and constraints; preserve provenance and blockers.
3. **Ideation output** — reused brief evidence/accepted direction or new step-3 gap work → §1 ¶3. Never require absent matrix cells or invent scores to satisfy the fresh-suite format.
4. **Channel outputs** (step 4) — reference-module patterns, doc/MCP/KB quotes → §1 ¶4 traceability only.

## Size-scaled counts — a range, not a quota

The template gives a typical range per section by size (`.size`): e.g. §4 1–3 US for XS/S, 3–8 for M+; §7 1–2 KPIs for XS/S, ≥3 for M+. Use the range to sanity-check the draft, never to pad it. The only **hard minimums** are the coverage floors (§5: ≥1 AC per coverage type and per retained US) and «every §2 goal has ≥1 US». An item added only to reach a number is filler — the critic flags it as F5.

- **§4** covers every glossary role the feature *involves* (named in the idea, §1, or an AC) — not every role the project glossary lists.
- **§6** keeps only the rows for quality aspects this feature changes or puts at risk; the placeholder rows are a menu, not a checklist.
- **§8** holds only genuinely open questions; `None.` is a valid, preferred outcome.
- **§8.1** holds the accepted assumptions-ledger entries (easy depth) and `assumption`-class brief evidence the spec relies on.

## §5 acceptance-criteria contract

AC describes a **business-observable outcome from the actor's perspective**, in Given/When/Then. **No upper cap** — propose as many as needed so **every §4 user story has ≥1 AC** and all five coverage types appear. If a `Drop` / `Save as Open Question` during Socratic leaves a coverage type empty **or a retained §4 user story with no AC**, regenerate a replacement AC and run a mini-batch on it (the two coverage floors, see [`socratic.md`](./socratic.md)). The «every US has ≥1 AC» rule is a **re-checked floor**, not only a draft-time target — it's verified after every §5 resolution, so `sequences` and `review` downstream can rely on each use-case having a testable criterion.

Five coverage types, ≥1 each:

1. **happy** — actor does the main flow → system records the outcome and confirms.
2. **error** — actor submits invalid input → system blocks it and explains the reason (phrase as «system shows the actor that <field> must be <constraint>»).
3. **authorization** — actor lacks permission (cross-tenant / cross-role / not-owner) → system denies access or hides existence; rationale in business terms.
4. **domain invariant** — actor violates a named invariant → system blocks the action and names the invariant in plain language.
5. **cross-context** — actor's action depends on state in another bounded context → system enforces the cross-context rule.

## Forbidden tokens in §5 AC (stack-agnostic, zero tolerance)

Checked by the critic's F6 and the regex scan over `spec.md` on disk:

- **HTTP verbs**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
- **URL paths**: anything starting with `/` then a lowercase identifier (`/orders`, `/items/{id}`, `/api/v1/...`).
- **status-code numerics** in the AC body: `200`, `201`, `400`, `401`, `403`, `404`, `409`, `5xx`, `500`, `503`.
- **error-code strings** matching `[a-z_]+\.[a-z_]+` (e.g. `order.not_owner`, `validation.title_too_long`).
- **JSON fragments / payload bodies**: `{title, description}`, `{id, status: "draft"}`.
- **SQL / DB constructs**: `UNIQUE(...)`, `FK`, raw `INSERT`/`SELECT`/`UPDATE`, constraint names — and any **driver/ORM-specific error type** (the stack-agnostic generalization of the old Go-only `pq.*`).

The technical mapping for all of these lives in `api` (HTTP method/path/status, error-code strings, payload schemas) and `data-model` / `decide-adr` (DB constructs). The spec's AC is WHAT a user can observe, not HOW the system encodes it.

## Stack-agnostic hygiene for §1–§3

The product-level sections must not name a **concrete technology** — a specific datastore, message broker, framework, or library. Those are `design` decisions. The old SDLC skill hard-coded a Go/Postgres regex (`Postgres|Redis|Kafka|JSONB`…); the stack-agnostic rule is: flag any proper-noun product/library name in the WHAT/WHY sections and move it to the design stage.

## Pre-write hygiene (before Socratic)

- §4 US roles use CONTEXT glossary terms verbatim.
- §3 Non-goals each carry a reason and fence something a reader could plausibly assume is in scope (no inventing).
- §5 AC headings use the exact coverage-type words (`happy` · `error` · `authorization` · `domain invariant` · `cross-context`).
- §1 ¶3 states the committed approach without losing the vector.
- §5 has ≥1 of each coverage type and 0 forbidden tokens (self-scan; the critic + regex are the backstop).
