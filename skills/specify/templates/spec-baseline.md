---
kind: baseline
status: Baseline
owner: "<area owner>"
reviewers: ["Tech Lead"]
updated_at: "<today YYYY-MM-DD>"
reflects_commit: "<short SHA of HEAD when scanned>"
---

# Baseline spec — <area>

<!-- instruction: a BASELINE records what the existing code does today, confirmed by its owner
(protocol → ../references/baseline.md). It never goes down the backbone: changes get their own
slug with `extends: <area>`. One-line links to inputs used:
> **Glossary:** [CONTEXT](./CONTEXT.md) (if present)
> **Architecture map:** `docs/architecture-map.md` §<module row> (if present)
> **Scanned:** the entry points / directories the explorer covered. -->

## 1. Context

<!-- instruction: 2–3 paragraphs, product language, no technology names.
¶1 What this area does today and for whom.
¶2 Why a baseline now — the change about to land in this area (name its slug when known).
¶3 (optional) What the scan did NOT cover (an entry point out of scope, generated code). -->

## 2. Purpose

<!-- instruction: 1–2 bullets — the outcome this area serves, as the owner confirmed it. -->

## 3. Boundaries

<!-- instruction: what this area does NOT do, where a reader might assume it does (each one sentence,
evidence-backed — «stock levels are owned by inventory; orders only asks for a reservation»). -->

## 4. User stories (observed)

<!-- instruction: one US per actor-facing capability the scan found. Roles from the glossary.

### US-NN: <3–6 word action title>
**As a** <role>
**I want** <action>
**So that** <observable benefit> -->

### US-01: <title>

**As a** <role>
**I want** <action>
**So that** <benefit>

## 5. Acceptance criteria (observed)

<!-- instruction: one AC per rule the code enforces. Heading:
### AC-NN (US-XX) — <happy · error · authorization · domain invariant · cross-context> · observed
Given/When/Then in business language. The forbidden-token rule of a normal spec applies unchanged
(no HTTP verbs, routes, status codes, error-code strings, JSON, SQL) — translate the code's
behaviour into what the actor observes. NO file paths here: evidence lives in §9.
Owner-confirm markers (baseline.md step 4): `<!-- known-defect: <expectation> -->`, `<!-- unconfirmed -->`.
The 5-coverage-type floor does NOT apply: a type the code lacks is a §8 row, never an invented AC. -->

### AC-01 (US-01) — happy · observed

**Given** <precondition>
**When** <action>
**Then** <outcome the actor observes today>

## 6. Non-functional behaviour (observed)

<!-- instruction: only numbers the code or config actually fixes (a timeout, a limit, a retry count)
with the anchor in §9. Nothing fixed → `N/A: not fixed by the current code`. -->

## 6.1 Security / privacy (observed)

<!-- instruction: data classification, personal data the area stores, the permission checks the
code runs today (or «none found» — which is also a §8 row). -->

## 7. Metrics

<!-- instruction: existing metrics/dashboards the area emits, if the scan found any; else `None found.` -->

## 8. Open questions & findings

<!-- instruction: every known defect, unconfirmed AC, and missing coverage type, each with owner + due.
`- [ ] <question or finding>. — owner: <role>, due: <date or «before <change-slug> design»>`. None → `None.` -->

## 9. Evidence

<!-- instruction: one row per §5 AC (and per §6 number). «Pinned by» = the existing test case that
exercises the rule, or `unpinned` — `tasks` turns unpinned rows the change touches into
characterization tasks. Every anchor must exist; an AC with no anchor is dropped. -->

| AC | Enforced at | Pinned by |
|---|---|---|
| AC-01 | `<path>:<line>` | `<test path>:<line>` / unpinned |
