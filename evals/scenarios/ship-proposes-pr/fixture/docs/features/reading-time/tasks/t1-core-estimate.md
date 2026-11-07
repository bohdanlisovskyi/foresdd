---
id: T1
layer: domain
deps: []
blocks: [T2]
acs: [AC-01, AC-02, AC-03]
files_hint: [readtime/core.py, tests/test_core.py]
context_budget: "S"
status: done
step: COMMIT
---

# T1 — Compute reading time and label from article text

## Why (user story)

US-1 — readers see «N min read» next to an article. *(spec §4)*

## Inlined context

200 words per minute, rounded up (ADR-0001). *(adr/0001)*

## Acceptance criteria

- AC-01, AC-02, AC-03 as in spec §5. *(spec §5)*

## Data delta

none

## API contract

none — library functions `minutes(text)`, `label(text)`.

## Definition of Done

minutes() and label() pass unit tests for exact, partial-minute and empty text.
