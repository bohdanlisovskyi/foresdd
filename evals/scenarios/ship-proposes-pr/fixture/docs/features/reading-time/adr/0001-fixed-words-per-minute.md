---
status: Accepted
date: 2026-10-22
---

# ADR-0001: Fixed 200 words per minute, rounded up

## Context and problem statement

Reading time must be predictable for readers and editors (spec §2). How do we turn a word count
into minutes?

## Considered options

1. Fixed 200 wpm, rounded up to a whole minute.
2. Fixed 238 wpm (research average), rounded to nearest.
3. Per-reader adaptive speed.

## Decision outcome

Chosen option 1: 200 wpm is the figure editors already quote, and rounding up never under-promises.

### Consequences

- Good: one constant, trivially testable, same label everywhere.
- Bad: fast readers see slightly pessimistic labels; changing the constant later changes every
  label at once.
