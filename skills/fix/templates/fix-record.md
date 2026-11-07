---
slug: <slug>
date: <YYYY-MM-DD>
triage: <regression | spec-bug | gap | no-spec | unreproduced>
acs: [<AC-NN>]            # the AC(s) traced; empty list for no-spec
commit: <sha>             # filled after the fix commit lands
recurrence_of: <none | _fixes/<date>-<short>.md>
from_review: <none | _review/review-<date>.md#<finding no.>>
---

# Fix: <one-line symptom>

## Symptom

<!-- The reproduction statement from intake, verbatim: «doing X, expected Y, got Z».
     Plus scope: who hits it (one user / all), since when (release, commit, date). -->

## Root cause

<!-- 2–4 sentences: the mechanism, the file:line, and why it slipped past the existing
     tests (no test at that level? a too-weak assertion? an untested branch?). -->

## The pinning test

<!-- Test name + level (unit / integration / e2e) + the failing line QUOTED from the RED
     run — the proof it failed for the right reason before the fix.
     No automated pin possible → the scripted manual reproduction (runnable steps) + why a
     test can't hold it.  unreproduced → what was tried, and under which conditions. -->

## Spec patch

<!-- One of, per the triage branch:
     (a) regression: «none — spec was right; AC-NN re-verified»
     (b) spec-bug:   the AC wording, before → after
     (c) gap:        the new AC text added to §5 (with its added-by-fix marker)
     no-spec:        «no spec to patch — brownfield; survey recommended»
     unreproduced:   «none — not reproduced; no fix applied» -->

## Follow-ups

<!-- Refactors / adjacent risks the fix exposed but deliberately did NOT touch (the fix
     commit stays minimal) — each as one actionable line. unreproduced → the instrumentation
     (log line, metric, assertion) that would catch the next occurrence. Or «none». -->
