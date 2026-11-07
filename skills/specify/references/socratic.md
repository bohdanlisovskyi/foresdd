# specify — delta over the shared Socratic loop

Read [`../../allocations/socratic-loop.md`](../../allocations/socratic-loop.md) for the canonical 4-state machine and edits-log, and [`../../allocations/write-and-commit.md`](../../allocations/write-and-commit.md) for the disk-write + commit discipline. specify supplies only the deltas below.

**Disk writes.** `spec.md` was bootstrapped from the template in step 1. Each walked section (§4, §5, §6, §7) is written into it the moment its last decision resolves; a `save_as_oq` row lands in §8 immediately. No commit here — the commits come once, after the critic + F6 scan (step 7).

**Progress.** Use the shared marker on every question (`§5 Acceptance criteria · decision 3/9 · section 2 of 4`; chip `§5 · 3/9`) — the four walked sections are §4, §5, §6, §7, so «section i of 4». Open the phase with the `▸ specify 6/7 · Validate §4–§7` banner and, before the walk starts, one line with the decision counts per section («§4 5 US · §5 11 AC · §6 3 NFR · §7 3 KPI — walking in that order»).

**Assumptions ledger → §8.1 (easy).** Run the shared ledger review once, after §7 and before the pass summary. Accepted entries are written to §8.1 Assumptions with their A-ids and risk tag; a vetoed or walked entry resolves as a normal decision in its section and never lands in §8.1. Ledger entries made earlier in the run (size/route in step 1c, the approach in step 3, deep-dive defaults) join the same review — one review per run, not one per phase.

## Sections walked (in order)

§4 User stories → §5 Acceptance criteria → §6 NFR → §7 KPIs. §1–§3 are drafted and shown but not per-item walked (they have no decision set — the user edits them inline if needed).

## Decision-types

- **User story** (§4) — Approve / Edit / Drop / Save-as-OQ. Dropping a US that owns the only AC of a coverage type triggers the §5 coverage gate.
- **Acceptance criterion** (§5) — the 4-state machine (4 options — the `AskUserQuestion` maximum). **Adding a new AC goes through the built-in «Other» free-text answer**: the question text ends with «To add a new AC, type it in "Other".» Text typed into «Other» on an AC question is a **new AC** (the current AC counts as Approved), never a rewrite — rewording the current AC is `Edit`. The skill drafts the new AC in business form and runs a one-question mini-batch on it, right after the current batch. The fast path's «Other» («approve all but #N») still works as described in the shared loop. Dropping / OQ-migrating the **last AC of a retained §4 user story** fires the use-case floor below (regenerate an AC for that US).
- **NFR row** (§6) — Approve / Edit (change the number or measurement) / Save-as-OQ (number is TBD, owner+due). A bare adjective («fast») is never Approvable — force a number or an OQ.
- **KPI** (§7) — Approve / Edit / Drop. baseline=TBD forces an inline measurement plan or an OQ.

## Per-skill gate — §5 coverage floors (two, both re-checked after every resolution)

After every §5 resolution, re-check **both** floors below (OQ-migrated AC do NOT count toward either — they live in §8 now). Both are the specify analogue of `design`'s blast-radius gate; both hold at every interview depth.

1. **Coverage-type floor.** ≥1 AC of each of the 5 coverage types (happy / error / authorization / domain invariant / cross-context) still stands after drops + OQ-migrations. If a type is empty, regenerate a replacement AC of that type and run a one-question mini-batch.
2. **Use-case floor (§4 US → ≥1 §5 AC).** **Every *retained* §4 user story still has ≥1 acceptance criterion.** If a Drop / OQ-migration leaves a retained US with no AC, regenerate (or let the user type one via «Other») an AC for that US and run a one-question mini-batch — a user story with no AC is incomplete and silently breaks the downstream `sequences` use-case coverage and `review`'s end-to-end trace. (Dropping the **whole** US is a legitimate de-scope and does not fire this floor — only a retained US losing its last AC does.) This also applies at **draft time**: if the initial §5 draft gave some §4 US no AC, add one before the walk begins.

## Open-Questions table

`save_as_oq` rows land in **§8 Open questions** as a checkbox line: `- [ ] <headline>? Default now: <…>. — owner: <…>, due: <…>` (the template's format). Owner + due mandatory; missing either downgrades to Drop. **Pre-fill the follow-up:** the owner+due capture question proposes a concrete owner (PM for scope/goal/KPI decisions, Tech Lead for AC/NFR decisions — or the named person if the conversation has one) and a stage trigger (`before foresdd:design` by default) as its «(Recommended)» option, so the common case is one click; «Other» takes a different owner/due. When the walk ends with no OQ rows, replace the template placeholder with `None.`
