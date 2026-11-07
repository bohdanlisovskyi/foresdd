# Rubric — fix pins a regression RED, fixes it GREEN, and commits fix + record separately

The fixture is a tiny Python stdlib package: `cart/totals.py` computes shipping with
`if subtotal_cents > FREE_SHIPPING_THRESHOLD_CENTS` (threshold 5000 cents), so a subtotal of
exactly 5000 is charged 499 — a real bug. `docs/features/free-shipping/spec.md` §5 **AC-01**
says «item subtotal is 50.00 **or more** → no shipping fee»: clear wording, violated by the code,
so the only correct triage is **(a) regression** (spec right, code wrong, no spec patch). The
fixture's own suite (`make test`, 6 tests) passes on the baseline — none of them probes the
5000 boundary. PASS requires ALL of:

1. **Triage = regression, citing AC-01.** The fix record's frontmatter has `triage: regression`
   and `acs:` containing `AC-01`, and the run's final message names the regression of AC-01.
   FAIL on `spec-bug`, `gap`, `no-spec` or `unreproduced`.
2. **RED test that fails on the baseline.** The diff adds at least one new test under `tests/`
   that asserts the boundary behaviour — a subtotal of exactly 5000 cents (or a cart totalling
   50.00) is charged no shipping / totals 5000 — i.e. an assertion the baseline `>` comparison
   makes fail. The final message (or the record's «The pinning test» section) quotes the failing
   line from the RED run (e.g. `AssertionError: 499 != 0`) and classifies it as a GOOD red.
   No pre-existing test in `tests/test_totals.py` is deleted or weakened.
3. **Minimal GREEN fix.** The only production file changed is `cart/totals.py`, and the change
   there is the boundary comparison (`>` → `>=`, or an equivalent ≤3-line change) — no
   refactor, no renamed functions, no other production file touched. The final message reports
   the gate green after the fix (`make test` and `make vet`, or the equivalent commands).
4. **Fix record.** Exactly one new file `docs/features/free-shipping/_fixes/<YYYY-MM-DD>-<short-slug>.md`
   exists with the template's sections — Symptom, Root cause (naming `cart/totals.py`), The
   pinning test, Spec patch, Follow-ups — and its «Spec patch» section states no patch was needed
   (spec was right; AC-01 re-verified). Its `commit:` field is filled with the fix commit's SHA
   (short or full), not the `<sha>` placeholder.
5. **No spec patch.** `docs/features/free-shipping/spec.md` is unchanged vs the baseline and no
   commit touches it (regression → nothing to patch).
6. **Separate commits with the contract's subjects and trailers.** After `baseline` there are
   exactly 2 commits:
   (a) the code fix — subject starts `fix: free-shipping `, touches only `cart/totals.py` and the
   test file(s) under `tests/`, and carries the trailers `SDD-Fix: <YYYY-MM-DD>-<short-slug>`
   (matching the record's file name without `.md`) and `SDD-AC: AC-01`;
   (b) the record — subject `fix: free-shipping record <YYYY-MM-DD>-<short-slug>`, touching only
   the `_fixes/` file, made after (a).
   Nothing is left uncommitted (`git status --porcelain` empty, `__pycache__` is gitignored).
7. **Handoff.** The final message ends with the stage-handoff block: a heading naming `fix` and
   `free-shipping`; *What I did* listing both commits with short SHAs and a `self-check:` line
   reporting the RED pin + gate result; *Review before continuing* linking the `_fixes/…md`
   record; *Run next* with a concrete next step — a `/foresdd:<stage> free-shipping` command or an
   explicit «nothing to resume» — not a vague «resume what you were doing».

FAIL if the triage is anything but regression, no new boundary test was added, production code
beyond the `cart/totals.py` comparison changed, `spec.md` was edited, the fix and the record share
a commit (or either is missing), the fix commit lacks `SDD-Fix` / `SDD-AC: AC-01`, or the
handoff block is missing.
