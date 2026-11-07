---
id: T2
layer: app
deps: [T1]
blocks: []
acs: [AC-03, AC-04]
files_hint: [readtime/__main__.py, tests/test_cli.py]
context_budget: "S"
status: done
step: COMMIT
---

# T2 — Expose the label through an editor CLI over a draft file

## Why (user story)

US-2 — editors run one command on a draft file. *(spec §4)*

## Inlined context

The CLI wraps `label()`; an unreadable file → stderr message + exit status 1. *(sad §8)*

## Acceptance criteria

- AC-03, AC-04 as in spec §5. *(spec §5)*

## Data delta

none

## API contract

none — CLI `python3 -m readtime <file>`.

## Definition of Done

python3 -m readtime <file> prints the label; an unreadable path exits 1 with a message.
