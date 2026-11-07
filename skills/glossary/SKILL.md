---
name: glossary
model: haiku
effort: low
agents: []
description: >
  Use to look up, capture, or maintain domain terms in CONTEXT.md before their meaning drifts —
  whenever a fuzzy word shows up in an interview, spec, or review and you want one canonical
  definition plus a NOT-reference so a homonym can't bite you in six months. Three modes: LOOKUP
  ("what is {X} in our domain", "what does {X} mean" — read-only, answers from both levels),
  ADD ("add term {X}", "define {X}", "add to CONTEXT", "/foresdd:glossary {term}" — up to four
  terms per question call), and EDIT ("fix the glossary", "change the definition of {X}",
  "rename {X} to {Y}", "make {X} project-wide", "remove {X}" — always shown as before → after and
  confirmed). Two-level contract: repo-root CONTEXT.md holds project-wide terms,
  docs/features/{slug}/CONTEXT.md holds feature-scoped ones; readers read both and the
  per-feature entry wins. Lazy-bootstraps the target from a template, checks BOTH levels for a
  conflicting entry, and never rewrites an entry without confirmation. Skip generic tech words
  (HTTP, queue, cache) — those are not domain terms. Output: created/edited CONTEXT.md (nothing
  in lookup mode). Runs anytime, no input gate; specify, clarify, design and api read its
  ## Glossary as the canonical source of role and domain-term names.
---

# Skill: glossary

Lazy utility that fixes the meaning of a domain term in `CONTEXT.md` the moment it first surfaces, so its sense doesn't drift across the pipeline. For each term it captures a one-sentence canonical definition and, when the word is ambiguous, a **NOT-reference** naming the concept it's confused with. Runs anytime, with no upstream gate: a quick «what does X mean here?», a single term mid-interview, an `undefined-term` finding `clarify` resolves mid-sweep, a batch handed over by `specify`, or a clean-up when a definition turned out wrong. The output feeds `specify` (role + domain-term names) and `design` (invariants), which treat `## Glossary` as canonical and override anything that contradicts it.

This is a capture utility, not a Socratic stage. It does **not** run the shared Socratic loop or critic. The one shared dependency is question phrasing:
→ [`../allocations/style.md`](../allocations/style.md)

## Owner

Whoever drives the conversation — anyone who spots ambiguity. Tech Lead approves the canonical form when a term is contested.

## Inputs

- `<term>` (one or more) — the domain word/phrase to look up, add, or edit. If not given: in lookup/add mode ask for it; in edit mode list the glossary entries and ask which one.
- (Optional) `<slug>` — feature slug; targets `docs/features/<slug>/CONTEXT.md`. Absent → repo-root `CONTEXT.md`.
- (Optional) `pending_glossary_terms` — a batch handed over by `specify` after it writes the spec.
- (Optional) an `undefined-term` finding from `clarify` — `clarify` invokes this skill **mid-stream**, one term at a time, the moment such a finding is Resolved (it never invents a meaning inline; the canonical definition lands here).
- (Optional) proposed phrasings already surfaced in an interview/brainstorm — offer them as definition options instead of asking blank.

## Shared rules (every mode)

- **The two-level contract.** Root `CONTEXT.md` = **project-wide** terms (meaningful across features); `docs/features/<slug>/CONTEXT.md` = **feature-scoped** terms (meaningful only inside that feature). A term lives in exactly **one** of the two files for a given feature, never split or duplicated across levels. Readers (`specify`, `clarify`, `design`, `api`) read **both** files; on a conflict the per-feature entry wins.
- **Finding a term.** An entry matches when its name, the text between `- ` and ` — `, equals the term case-insensitively. Simple singular/plural variants count as the same term (`tenant` = `tenants`). A prefix is **not** a match: `tenant` does not match `tenant-admin`. Entries whose name *contains* the term, or whose NOT-reference mentions it, are **related**. They are shown, never treated as the same entry.
- **The entry format.** `- <term> — <one-sentence definition>. NOT <confused concept + how it differs>.`, or `- <term> — <definition>.` when there is no plausible homonym.
- **Only `CONTEXT.md` files are written.** Other artifacts that use a term (`spec.md`, `sad.md`, …) are reported to the user, never edited here.

## Protocol

### 0. Pick the mode

Read the request:
- A question about meaning («what is X», «what does X mean», «is X the same as Y», «show the glossary») → **Lookup**.
- A change to something already there («change / fix / correct the definition of X», «rename X to Y», «X is project-wide», «move X to <slug>», «remove / drop X», bare «fix the glossary») → **Edit**.
- Otherwise («add term X», «define X», a `specify` / `clarify` hand-over) → **Add**.

An add request for a term that already exists turns into an edit offer (Add step 3). A lookup that finds nothing offers to add the term (Lookup step 2). The user never has to know the mode names.

### Lookup mode — read-only

1. **Read both levels.** Root `CONTEXT.md` plus `docs/features/<slug>/CONTEXT.md` when `<slug>` is given. Without a slug, also scan `docs/features/*/CONTEXT.md` so a feature-scoped definition isn't missed.
2. **Answer.**
   - **Found** → quote the entry verbatim with its file. When both levels hold it, show both and say which one wins for `<slug>` (per-feature). If it's only feature-scoped and no slug was given, name the feature(s) it belongs to. Add the related entries (name + file) on one line when any exist.
   - **Not found** → say so, list the related entries if any, then ask ONE question: `Add it now` / `Not now`. `Add it now` → continue in **Add mode** from step 2 with this term (and the slug, if any).
   - «Show the glossary» with no term → print the `## Glossary` entries of each level under its file name, plus a count.
3. **No writes, no commit, no stage-handoff block.** A lookup is an answer, not a stage. Stop here unless the user chose `Add it now`.

### Add mode

1. **Pick the target.** `<slug>` given → the per-feature file; otherwise → repo-root.
2. **Generic-term filter.** Reject words that name infrastructure or transport rather than the business domain (HTTP, queue, cache, the datastore, the broker, a framework): «`<term>` is technical, not a domain word — its choice belongs in the SAD or an ADR, not the glossary». **The user can overrule**: if they say the word carries a business meaning in this project (a call-centre «queue» of waiting customers), accept it and say so in the handoff. In a batch, refuse the technical terms in one line and continue with the rest.
3. **Conflict check — both levels.** Search the target and the other level's file (root ↔ `docs/features/<slug>/CONTEXT.md`) per «Finding a term».
   - Found, identical sense → that term is done: report «already in the glossary» + which file holds it. Offer `Edit it` only if the user's wording differs from the stored one.
   - Found, different sense → ask (phrasing per [`../allocations/style.md`](../allocations/style.md)): «`<term>` is already defined as `<existing>` in `<file>` — same concept or a different one?». Same concept but better wording → switch to **Edit mode** (redefine) for that term. Different: a genuinely feature-scoped narrowing goes to the per-feature file (readers let it win there); otherwise propose a disambiguating pair of names (e.g. a billing-scoped vs a runtime-scoped variant) and fix both through Edit mode.
   - Not found in either → continue.
   Batch: run the check for every term first, then pack the conflict questions like step 5 (≤4 per call).
4. **Bootstrap (lazy).** `test -f <target>`. Missing → copy [`./templates/CONTEXT.md`](./templates/CONTEXT.md) to `<target>`, fill the `# Domain Context — …` heading with the slug (or the repo name for root), and **delete the template's placeholder bullets** (`- <term> — …`, `- <invariant …>`, `- <out-of-scope …>`). Present → read it.
5. **Ask the definition and the NOT-reference — packed, up to 4 questions per call.** Each term needs two answers: «Define `<term>` in this domain, in one sentence» and «Which concept does `<term>` get confused with, so a future reader doesn't mix them up?» (`None` is a valid answer). The two questions for a term **always ride in the same call**, so one `AskUserQuestion` call covers **two terms**. One term = one call; four terms = two calls, never eight. Offer interview/brainstorm phrasings as the options when available. When there are none, the user types the definition through «Other». For the NOT-reference, offer the plausible homonyms you can see in the spec or the existing glossary, plus `None`. Sessions without `AskUserQuestion`: one numbered plain-text message holding the same questions for up to four terms, then stop and wait for one reply.
   *Packing questions is not deferring capture.* `specify` and `clarify` still call this skill the moment a term surfaces. Packing only applies to terms that are already waiting together (a `pending_glossary_terms` batch, or «add tenant, seat and plan»).
6. **Compose one line per term** in the entry format.
7. **Append under `## Glossary`.** Insert each line in `## Glossary` (alphabetical if the section is already sorted, else at the end). Never rewrite an existing entry in this mode.
8. **Prune empty H2s — only the ones this run created.** On a fresh bootstrap, delete `## Invariants` / `## Out of scope` if they hold no real content. Only `## Glossary` is mandatory. Never delete a heading the user already had. (A genuine invariant or out-of-scope note goes in its section, never as implementation detail.)
9. → **Finish** (below).

### Edit mode — always before → after, always confirmed

1. **Find the entry** at both levels per «Finding a term». Not found → say so, list related entries, and offer `Add it instead` (→ Add mode step 2) / `Cancel`. Bare «fix the glossary» with no term → list the entries (both levels, with file) and ask which to edit. Up to 4 entries go in one question with `multiSelect`; more than that, ask for the name in free text.
2. **Pick the operation.** It usually follows from the request; when it doesn't, ask once: `Change the definition / NOT-reference` · `Rename` · `Move to the other level` · `Remove`.
   - **Redefine** — ask for the new wording exactly as Add step 5 (only the half that changes, if the user said which).
   - **Rename** `<old>` → `<new>` — run the Add step 2 filter and step 3 conflict check on `<new>`. Then search the term's usages across `docs/` and both `CONTEXT.md` levels with a whole-word, case-insensitive search. List them as `file:line`, capped at 10 with a «+N more» count.
   - **Move** — feature → root («this is project-wide now») or root → feature («only <slug> means this»). On a promotion to root, also check every other `docs/features/*/CONTEXT.md` for the same term and list any hits: those entries now narrow the root one.
   - **Remove** — search usages as for rename. A term still used in a `spec.md` / `sad.md` gets a warning: removing it leaves those documents with an undefined term.
3. **Show before → after and confirm — ONE question.** The question text shows the exact lines: the old entry, the new entry, the file(s) each lives in, and, for rename/remove, the usage list. Options: `Apply` (Recommended) / `Adjust` (re-asks the wording) / `Cancel` (nothing is written). On a rename, the NOT-references that name `<old>` inside the `CONTEXT.md` files are part of the same change and are shown in the preview. Usages in other artifacts are only listed.
4. **Apply** — replace or remove exactly the confirmed lines; keep the rest of each file byte-identical. A move is one remove + one add, in the same run. If the target file is missing, bootstrap it per Add step 4.
5. → **Finish** (below). In *Run next*, when usages were listed outside `CONTEXT.md`, point at the stage that owns them (e.g. `/foresdd:clarify <slug>` to bring `spec.md` in line).

### Finish (add + edit)

1. **Stamp** `updated_at: <today>` in the frontmatter of every changed `CONTEXT.md`.
2. **Structural self-check** — per [`../allocations/self-check.md`](../allocations/self-check.md): re-read the changed file(s) from disk and verify **3 items**:
   1. **Placement.** Every term added, redefined, moved or renamed-to appears **exactly once across root + `docs/features/<slug>/CONTEXT.md` combined**. A removed or renamed-from term appears **zero** times.
   2. **Format.** Each touched entry matches `- <term> — <definition>.`, with the optional `NOT …` tail.
   3. **No leftovers.** No template placeholder (`<term>`, `<invariant`, `<out-of-scope`, `<slug or repo>`) remains, no H2 this run created is empty, and `## Glossary` is present.
   Fix + re-check ≤2 cycles; surface anything unresolved.
3. **Commit** per [`../allocations/write-and-commit.md`](../allocations/write-and-commit.md) — after the self-check, one commit per changed `CONTEXT.md`. Subjects: add `glossary: <slug> CONTEXT.md + <term>` (a batch lists the terms) · redefine `glossary: <slug> CONTEXT.md ~ <term>` · rename `glossary: <slug> CONTEXT.md <old> → <new>` · remove `glossary: <slug> CONTEXT.md − <term>` · move: one commit per file, e.g. `glossary: CONTEXT.md + <term> (promoted from <slug>)` and `glossary: <slug> CONTEXT.md − <term> (promoted to root)`. Repo-root file: drop the `<slug>` (`glossary: CONTEXT.md + <term>`). Invoked in-flow by `specify` / `clarify` → don't commit here; the caller commits `CONTEXT.md` as its own document at the end of its step.
4. **Handoff** — **emit the stage-handoff block** per [`../allocations/handover.md`](../allocations/handover.md) (utility variant). *What I did* covers what changed per term (added / already present / refused as technical / redefined / renamed / moved / removed), any overruled generic-filter refusal, and «self-check: 3/3 pass». *Review* lists the changed `CONTEXT.md` file(s). *Run next* is the stage that owns any listed usages, else resume your backbone stage (e.g. `/foresdd:design <slug>`); `/clear` optional.

## Definition of Done

- **Lookup:** the answer quotes the stored entry and its file (or says there is none and offers to add it). Nothing on disk changed.
- **Add:** `<target>` exists and contains each new term under `## Glossary` in the «one-sentence canonical + optional NOT-reference» format. Terms already present were reported, not duplicated. Generic tech words were refused unless the user overruled.
- **Edit:** the user saw before → after (plus usages for rename/remove) and confirmed. Only the confirmed lines changed, and the term is placed exactly once across both levels (or zero times after a remove/rename).
- Any conflict with an existing entry is resolved (reported as duplicate, or disambiguated into distinct names).
- No template placeholder remains; empty H2 sections this run created are pruned; `## Glossary` remains.
- `updated_at` reflects today on every changed file. A standalone run commits each changed `CONTEXT.md` after the self-check; an in-flow call leaves the commit to its caller.

## Anti-patterns

- **Glossary as spec or scratch pad.** Implementation detail («counter stored with a 1-minute TTL») belongs in the SAD/ADR, not here.
- **Empty H2 «for completeness».** A heading with no bullets that this run created — prune it.
- **Silent edits.** Adding a term without confirming the definition, or changing an entry without showing before → after. The author must control the glossary.
- **Writing during a lookup.** «What is X?» is answered from the files. Nothing changes unless the user picks `Add it now`.
- **Deferring capture.** «I'll add them later» loses the term. Capture it when it surfaces. Packing questions for terms that are already waiting together is fine; holding terms back to build a batch is not.
- **One call per question in a batch.** Two terms per call (definition + NOT-reference each), up to four questions.
- **Storing generic tech words.** HTTP, queue, the datastore name — refuse them unless the user says the word means something in the business.
- **Prefix matching.** `tenant` is not `tenant-admin`. Match the whole entry name.
- **Rewriting other artifacts on a rename.** List the usages in `spec.md` / `sad.md` and point at the owning stage. This skill writes only `CONTEXT.md`.
- **Ambiguous term with no NOT-reference.** A homonym without «NOT …» is a six-month confusion waiting to happen.

## References & template

- [`./templates/CONTEXT.md`](./templates/CONTEXT.md) — output scaffold; inline comments are the per-section contract (Glossary mandatory, Invariants/Out-of-scope pruned when empty, placeholder bullets deleted on bootstrap).
- [`../allocations/style.md`](../allocations/style.md) — phrasing for the definition / NOT-reference / conflict / confirm questions.

## Example invocations

> **User:** «add term tenant for rate-limiting-per-user»
> **Skill:** Add mode. `<slug>` given → target `docs/features/rate-limiting-per-user/CONTEXT.md`. Generic filter: `tenant` is domain → continue. Search both levels → not found. File missing → copy template, fill the heading, delete the placeholder bullets. ONE call, two questions: definition → «a billable customer organisation owning 1+ users»; NOT-reference → «user — a user is one person inside a tenant». Compose `- tenant — a billable customer organisation owning 1+ users. NOT user (a user is one person inside a tenant).` → append under `## Glossary` → prune empty `## Invariants`/`## Out of scope` → `updated_at: 2026-05-28` → self-check 3/3 → commit `glossary: rate-limiting-per-user CONTEXT.md + tenant`.

> **User:** «what is a seat in our domain?»
> **Skill:** Lookup mode. Reads root `CONTEXT.md` + `docs/features/*/CONTEXT.md` → found only in `docs/features/billing-v2/CONTEXT.md`: «`- seat — one paid licence slot a tenant assigns to a user. NOT user (a seat can be empty).`» — feature-scoped to `billing-v2`; related: `seat-pool` (same file). Nothing written.

> **User:** «tenant is project-wide now, not just rate limiting»
> **Skill:** Edit mode → Move (feature → root). Checks other features → `billing-v2/CONTEXT.md` has no `tenant`. Confirm: «Move `- tenant — a billable customer organisation owning 1+ users. NOT user (…)` from `docs/features/rate-limiting-per-user/CONTEXT.md` to `CONTEXT.md`?» → `Apply` → removes it from the feature file, appends it to root → self-check 3/3 (tenant appears exactly once) → commits `glossary: CONTEXT.md + tenant (promoted from rate-limiting-per-user)` and `glossary: rate-limiting-per-user CONTEXT.md − tenant (promoted to root)`.
