# Structural self-check — the final-step verification contract every skill runs

> **Reference-only.** Not a skill. Every skill verifies its own output before handing off —
> this file is the one contract for how. A skill either runs a **named structural checklist**
> (defined in its own SKILL.md, penultimate protocol step) or maps an existing heavy verifier
> onto this contract (see «Heavy verifiers count» below). Either way, the SKILL.md names the
> phrase **structural self-check** at the place where the contract is satisfied — that is the
> greppable evidence the validator enforces.

## The contract (five steps)

1. **Re-read the artifact from disk.** Never check the in-memory draft — the file as written is
   what downstream stages read. (A skill that writes nothing on a given run — e.g.
   `interview` outside a git repo — checks its emitted output against its DoD instead.)
2. **Run the named checklist.** Each item is **structural and cheap to verify** — a grep, a count,
   a file-exists test, an enum membership — not a judgment call. The checklist lives in the skill's
   own SKILL.md (penultimate protocol step) and has a fixed item count, so the result is reportable
   as `N/N`. Every item carries a **short label** (2–4 words, e.g. «frontmatter stamped», «AC
   coverage», «DAG acyclic») — the label, never a bare number, is what the user sees when it fails.
3. **Fix + re-check, ≤2 cycles.** A failing item is fixed and the checklist re-run. Two fix cycles
   maximum — an item still failing after that is *unresolved*, not retried forever. See «Auto-fix
   boundaries» for what a fix may touch.
4. **Surface the unresolved — never silently.** Anything still failing goes to the user per
   «When an item stays unresolved» below. Silently committing a failing artifact is the one
   forbidden move; a stated failure is acceptable, a hidden one is not.
5. **Report in the handoff.** *What I did* carries exactly one self-check line in the fixed format
   below — on a pass as well as a failure.

**Order: self-check → commit → handoff.** The self-check runs **before** any commit
([`write-and-commit.md`](./write-and-commit.md)): a pass unlocks the step's per-document commits; an
unresolved item means zero commits (unless the user explicitly overrides — see below) — the files
stay on disk, uncommitted, and the handoff says why.

## The handoff line (fixed format)

One line in *What I did*, in fixed English whatever the conversation language (it is greppable
proof, like the handoff headings):

| Outcome | Line |
|---|---|
| Clean pass | `self-check: 6/6 pass` |
| Pass after auto-fixes | `self-check: 6/6 pass (auto-fixed: updated_at stamped, AC coverage row added)` |
| Pass with a degraded item | `self-check: 6/6 pass (degraded: mermaid syntax — mmdc unavailable, structural lint only)` |
| Unresolved | `self-check: 5/6 — AC coverage unresolved (not committed)` |
| Heavy verifier | `self-check: critic 0 open + 2/2 structural pass` · `self-check: GATE green (unit, lint, vet)` · `self-check: drift 0 + 1/1 structural pass` |

- **Name items by label**, never «item 4».
- **Never «see above».** The details of an unresolved or degraded item live in *⚠ Needs your
  attention* in the same handoff block ([`handover.md`](./handover.md)) — the user should not
  scroll back through the run to find them.
- A **degraded** item ran a weaker check because a tool was missing (e.g. `mmdc` → structural
  mermaid lint). It counts as passed if the weaker check passed, but it is always named in the
  line **and** in *Needs your attention* («install `mmdc` for full validation»).

## Auto-fix boundaries

The fix cycle repairs **structure**, not decisions the user already made.

- **Fix silently-but-reported:** mechanical, derivable items — a missing frontmatter stamp, a
  wrong date, a duplicate `.gitignore` line, a coverage-table row whose content is already
  decided elsewhere in the artifact, a broken relative link, mermaid syntax.
- **Ask instead of fixing:** anything that would change content the user confirmed in the
  Socratic walk or an `AskUserQuestion` — an AC's wording, a decision, an ADR outcome, a scope
  line. Ask one `AskUserQuestion` with the proposed fix; a «no» makes the item unresolved.
- **Every auto-fix is listed** in the handoff line's `(auto-fixed: …)` suffix by item label. The
  file changed after the user last saw it — they must know where to look.

## When an item stays unresolved

1. **Status `⚠️`, not `⛔`.** The artifact is written; the stage finished with a caveat.
   (`⛔` is for a stage that stopped *before* writing its artifact — [`handover.md`](./handover.md).)
2. **One *Needs your attention* bullet per unresolved item:** label + what's wrong (with the
   path/line) + what the two fix cycles tried + the action to take.
3. **Offer the way forward** with one `AskUserQuestion` (interactive runs only):
   - **I'll fix it — re-check** — the user edits the file; the skill re-reads from disk and re-runs
     the full checklist once (a fresh check, not a third fix cycle). Pass → commit normally.
   - **Commit anyway** — an explicit override: commit per [`write-and-commit.md`](./write-and-commit.md)
     with the body line `self-check override: <item label>`, and keep the *Needs your attention*
     bullet.
   - **Leave uncommitted** — the default: files stay on disk; the handoff gives the exact
     `git add -- <paths> && git commit -m "<planned message>"` commands for later.
   Headless / non-interactive / Plan Mode → no question; take **Leave uncommitted**.

## Nested runs (a skill invoked by another skill)

When a skill runs **inside** another skill's step (e.g. `glossary` called from `clarify`, a
`decide-adr` spawned mid-`design`), the **inner** skill still runs its own checklist, but it does
**not** print a separate handoff. It returns its result to the caller, and the **outer** skill
reports it as a second line in its own *What I did*:
`self-check (glossary): 3/3 pass`. An inner unresolved item makes the outer status `⚠️` and
blocks the commit of the inner skill's document only — the outer skill's own documents commit
normally if their own check passed.

## Heavy verifiers count (no double work)

A skill that already runs a heavy verifier — the clean-context **critic** (`specify`, `design`),
the **reviewer** agent (`review`), the **devil's-advocate** sweep (`clarify`), the bidirectional
**drift check** (`api`), the **mermaid re-validation** + coverage table (`sequences`), the
4-mandatory **self-check** (`data-model`, `tasks`), the per-task **GATE** (`implement`, `fix`) —
counts that verifier **as** its structural self-check. It does not bolt a second checklist on top;
it adds **only the structural items the verifier doesn't cover** (e.g. «frontmatter stamped»,
«file at the size-correct target») and still reports per step 5. The SKILL.md states the mapping
in one literal sentence («<verifier> = this skill's structural self-check»).

The handoff line names the verifier and its own outcome unit, then the structural leftovers:
`self-check: <verifier> <outcome> + <n>/<n> structural pass` — e.g. `critic 0 open` (findings
left open after resolution), `reviewer PASS`, `GATE green (unit, lint, vet)`, `drift 0`. A
verifier with no structural leftovers omits the `+ …` part.

## Anti-patterns

- **Judgment items in the checklist.** «The spec is clear» is not checkable; «every §5 AC id
  appears in the coverage table» is. Judgment belongs to the heavy verifiers.
- **Checking the draft, not the disk.** The bug this contract exists to catch is the write that
  didn't land the way the conversation assumed.
- **Committing first, checking after.** A commit marks a checked document; a failing check after
  the commit leaves broken history.
- **Endless fix loops.** Two cycles, then surface. A checklist that can't converge in two fixes is
  flagging a real problem the user must see.
- **A silent pass.** The handoff line is mandatory even when everything passes — «self-check: 6/6
  pass» is one line of proof, not noise.
- **A silent auto-fix.** Changing the file after the user reviewed it without saying so — every
  fix is named in `(auto-fixed: …)`.
- **Rewriting a confirmed decision to make a check pass.** Ask; a check never outranks the user.
- **«See above» / «item 4 failed».** The failure is stated in *Needs your attention*, by label.
- **Duplicating the heavy verifier.** If the critic already checked cross-section drift, the
  checklist doesn't re-check it — only the structural leftovers.
