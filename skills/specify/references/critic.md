# specify — delta over the shared critic

Read [`../../allocations/critic.md`](../../allocations/critic.md) for the canonical dispatch (`subagent_type: "foresdd:critic"`, fallback `general-purpose` with the same prompt; clean context), the F1–F6 skeleton, the outcomes table and the resolution flow. specify supplies only the deltas below; the skill fills the placeholders and dispatches.

## Placeholders

- **`{{ARTIFACT_NAME}}`** = "Product spec (context / goals / user stories / acceptance criteria / NFRs / KPIs)".
- **`{{DRAFT_PATH}}`** = `docs/features/<slug>/spec.md` — the critic Reads the file from disk (it was written section by section); the skill patches that file with the findings the user accepts.
- **`{{EDITS_LOG}}`** = the step-6 edits-log.
- **`{{EXTRA_INPUTS}}`** = the current owner corrections (verbatim) when an idea brief was reused; else `none`.
- **`{{UPSTREAM_FILES}}`** (the critic Reads these itself):
  - `CONTEXT.md` (repo root) **and** `docs/features/<slug>/CONTEXT.md` — canonical glossary (roles, domain terms), each if present; per-feature wins on conflict.
  - `docs/idea-brief.md` when reused, plus the current owner corrections supplied in the prompt.
  - any reference module / doc the user named in step 4 (paths only).
  - `docs/features/<slug>/.size` — the declared size class (F2; written in step 1).
- **`{{F5_FLOOR}}`** = the F5 section below. **`{{F6_RULES}}`** = the F6 section below. **`{{EXTRA_PROBES}}`** = the brief-preservation check (only when a brief was reused) + the F1 specialization below.
- **Override slot** = `spec.md` §1 ¶4 («Decision override» bullets).

## F5 structural floor → `{{F5_FLOOR}}`

- §4 holds ≥1 US per glossary role **the feature involves** (named in the idea, §1, or any AC — not every role in the project glossary) + per §2 goal.
- §5 holds ≥1 AC of each of the 5 coverage types **after** drops + OQ-migrations, each heading tagged with the exact coverage-type word.
- §6 NFR rows all carry a numeric target + measurement (no adjectives, no lone TBD); a leftover template placeholder row (`<N ms>`, `<metric source>`) is a finding.
- §8 Open Questions has a row for every `save_as_oq` with owner + due; an empty §8 reads `None.` (no surviving template placeholder).
- §8.1 Assumptions: no `high` assumption silently decides an AC outcome that the user never saw — the ledger review must have shown it.
- **Filler** (fix-type `amend`, severity `should`): a non-goal nobody would assume is in scope, a US for a role no AC or goal needs, an OQ whose answer is already in the spec, an NFR row for an aspect this feature doesn't touch. Size-scaled counts are ranges; padding to reach one is a defect, not compliance.
- Frontmatter `reviewers` includes `Security Lead` iff §6.1 says `Security review: Required`.

## F6 specialization — forbidden-token leak (the load-bearing check) → `{{F6_RULES}}`

This is specify's primary F6. Scan §5 AC text for the forbidden tokens in [`draft-generation.md`](./draft-generation.md) (HTTP verbs, URL paths, status numerics, `module.error_name` strings, JSON fragments, SQL/driver constructs). **List every hit** — grouped as one F6 finding for §5, one sub-bullet per AC line (fix-type `mechanical` when the business-form rewrite is unambiguous, else `amend`):

```
- **[C{n} · should · F6] {k} AC lines contain forbidden tokens** — where: §5; caused by: —; contradicts: draft-generation.md forbidden-token list; fix: mechanical — rewrite into business form (actor-observable outcome) OR move the HTTP/error/schema detail to `api`; before: —; after: —.
  - AC-NN: "<verbatim snippet>" (hits: <token1>, <token2>) → "<business-form rewrite>"
```

Also flag any concrete technology name (datastore / broker / framework / library) appearing in §1–§3 — those belong to `design`.

## Brief preservation check → `{{EXTRA_PROBES}}`

When interview was reused, check the draft against its accepted scope/constraints, rejected
alternatives, evidence limits, and current owner corrections per [`brief-reuse.md`](./brief-reuse.md).
Do not demand new competitive tables or RICE/matrix cells for already covered decisions. Flag
an unverified claim promoted to fact, a blocking unknown silently answered, or a confirmed
constraint dropped during product-level rephrasing. Technical detail stays traceable in the
brief/design source; its absence as a technology name in an AC is not itself lost scope.

## F1 specialization — approach drift → `{{EXTRA_PROBES}}`

If the edits-log dropped/edited a US or AC tied to the committed approach in §1 ¶3, check that §1 ¶3 still states that approach accurately. A spec whose body no longer matches its own «committed approach» paragraph is drift.
