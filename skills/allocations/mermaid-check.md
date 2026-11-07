# Mermaid check — validate every diagram after writing it

> **Reference-only.** Not a skill. Any skill that emits a Mermaid diagram runs this **after
> writing** the diagram and **before committing** it. The rule: a diagram that doesn't parse is
> never committed — broken Mermaid renders as a red error box (or, for a misspelled C4 keyword,
> a silently empty box) for the reader.
>
> This file answers «does it parse?». How to *show* the diagram to the user is
> [`diagram-presentation.md`](./diagram-presentation.md); whether to ask per diagram is
> [`interview-depth.md`](./interview-depth.md).

## Procedure

1. **Write** the diagram into its file. Note the line of each ```mermaid fence **you** wrote or
   changed this run — that is your **scope**.
2. **Validate** — run both checks below over the file, scoped to your blocks. Batch: one run per
   file after all its diagrams are written, not one run per diagram.
3. **On failure — fix syntax only, then re-validate. At most 2 fix cycles.**
   - A fix may change **syntax only**: quoting a label, renaming a reserved id (`end` → `done`),
     reordering a declaration above its first `Rel`, closing a block, rewording a `;` out of
     message text. It must **never** add, drop, merge or re-route a participant, node, edge or
     branch.
   - If the only fix that parses would change what the diagram *says*, it is not a syntax fix —
     stop and go to step 4 (per [`self-check.md`](./self-check.md) §Auto-fix boundaries: content
     the user confirmed is asked about, never silently changed).
   - Every applied fix is listed in the handoff's `(auto-fixed: …)` suffix (e.g.
     `auto-fixed: mermaid syntax — quoted 2 flowchart labels in ux-flows.md`).
4. **Still failing after 2 cycles → ask, never ship it.** Show the user the problem in plain words
   (below), then one `AskUserQuestion`:
   - **Fix it myself** — leave the file uncommitted, tell them the exact `path:line`, and wait.
   - **Drop this diagram** — remove the block; the surrounding prose stays; record the drop in
     *Needs your attention*.
   - **Commit with a TODO** — keep the block, prepend a `%% TODO: does not parse — <error>` line,
     and report the self-check item as **unresolved** (`self-check: N-1/N — mermaid syntax
     unresolved`). Only on explicit choice; never the default.
   - **Show the source** — print the raw block once, then re-ask the same three options.

   Headless / no human can answer (per [`fallbacks.md`](./fallbacks.md)) → do not commit the
   file; report the block and error in the handoff's *Needs your attention*.

### How to report an error to the user

Never paste a raw parser trace as the explanation. Give **`path:line` in the file** (not the line
inside the block), the **diagram type**, the cause in one plain sentence, and the fix you tried:

> `docs/features/prefs/sad.md:142` (sequence «save preferences»): the `;` in the note text ends
> the statement early, so the rest is read as a broken message. Tried replacing it with «, and» —
> still failing because the `alt` opened at line 136 is never closed.

## The two checks

### 1. Structural lint — always runs

A stdlib-only Python script ships next to this file, at `scripts/mermaid_lint.py` (resolve it from
the directory you read this file from — in an installed plugin that is
`<plugin root>/skills/allocations/scripts/mermaid_lint.py`):

```bash
python3 <allocations dir>/scripts/mermaid_lint.py docs/features/<slug>/sad.md --only 120-180
```

- `--only N-M` (repeatable) — only blocks whose opening fence falls in those lines can fail the
  run. Pass one range per block you wrote. Omit it when you wrote the whole file.
- Output is one finding per line, already in user-facing form:
  `path:line: error|warning [type] cause — fix hint`, then a summary
  (`mermaid-lint: 3 block(s), 0 error(s), 1 warning(s)`).
- Exit `0` = no in-scope errors (warnings are reported, never block) · `1` = in-scope errors ·
  `2` = bad usage or unreadable file (a tool problem — report it, don't treat it as a pass).
- `--list` prints every block's fence line + type (handy for mapping an `mmdc` error, below).

It runs **even when `mmdc` is installed**: it enforces house rules a real parser accepts —
leftover `<placeholder>` text (the `sequences` generic participants `<client>`, `<ui>`, `<user>`,
`<service>`, `<data-store>`, `<external-system>`, `<message-bus>` are allowed), C4 elements
declared before their `Rel`, misspelled C4 boundaries that render as an empty box.

### 2. Full parse with `mmdc` — only when installed

If `mmdc` (mermaid-cli) is on `PATH`, also run the real parser. **Never download it** —
no `npx @mermaid-js/mermaid-cli` (it pulls Chromium, hundreds of MB, and stalls offline). Write the
throwaway output to a fresh temp dir and remove it — `mmdc` writes one SVG per block next to the
output path:

```bash
out=$(mktemp -d) && mmdc -q -i docs/features/<slug>/sad.md -o "$out/check.md" 2>&1; rc=$?; rm -rf "$out"; echo "exit=$rc"
```

Non-zero exit = a block failed. `mmdc` stops at the first failing block, and its `Parse error on
line N` counts from the block's first line: map it to the file with `mermaid_lint.py --list`
(failing block = number of rendered SVGs + 1; file line = that block's fence line + N). Report it
in the form above.

`mmdc` checks the whole file. If the failing block is **outside your scope** (a pre-existing
diagram), don't block on it and don't fix it: name it under *Needs your attention* («pre-existing
diagram at `sad.md:88` does not parse») and continue.

### When `mmdc` is not installed

The lint alone is the check. That is a **degraded** item per [`self-check.md`](./self-check.md):
`self-check: N/N pass (degraded: mermaid syntax — mmdc unavailable, structural lint only)`, plus
**one** line in *Needs your attention* per run — not per diagram:
«install mermaid-cli for a full parse: `npm i -g @mermaid-js/mermaid-cli`».

## Per-type gotchas (the usual render failures)

The lint flags each of these; this list is what to write correctly in the first place.

- **C4** (`C4Context` / `C4Container`): it's `Container_Boundary` / `System_Boundary` (NOT
  `Container_Bondary`, NOT `ContainerBoundary` — those render an empty box, no error); declare every
  `Person(...)` / `System(...)` / `Container(...)` / `ContainerDb(...)` **before** any
  `Rel(from, to, "label")` that uses its id; ids have no spaces; `Rel` needs the quoted label arg.
  Full syntax → [`../design/references/c4-mermaid-syntax.md`](../design/references/c4-mermaid-syntax.md).
- **sequenceDiagram**: declare `participant X as Display Name`, then refer to `X` (implicit
  participants are legal, but declaring fixes the column order); keep `alt … else … end` /
  `loop … end` / `opt … end` / `par … and … end` balanced; `Note over X,Y: text`. **No `;` in
  message/Note text** — `;` is a statement separator, so `Note over R,DB: commit; any error rolls
  back` parses the rest as a broken message (a real bug this check caught). Avoid **Unicode arrows
  (`→`)** in text (use words), and put **no trailing `%%` comment** on a statement line (`%%` starts
  its own line).
- **erDiagram**: `ENTITY ||--o{ OTHER : "label"`; attribute lines are `type name` inside
  `ENTITY { … }`; cardinality glyphs must be valid (`||--o{`, `}o--||`, `|o..o|`, …). The key class
  is `PK` / `FK` / `UK` only — **`PK_FK` is invalid** (write `PK, FK`; another real bug this check
  caught).
- **flowchart** (`flowchart LR` / `TD`, also used by `ux-flows`, `tasks`, `roadmap`): `A[label] -->
  B{decision}`; match bracket shapes (`[]` `()` `{}` `[[ ]]` `[( )]` `{{ }}`). Implicit nodes are
  legal. Common breakages:
  - a **lowercase `end`** used as a node id ends the flowchart — use `End` / `done`;
  - a label with brackets or other special chars needs quotes: `A["call (x)"]`; a literal quote
    inside a quoted label is `#quot;`;
  - an edge glued to an id starting with `o`/`x` (`A---oB`) becomes a circle/cross edge — add a
    space or rename;
  - every `subgraph` needs its `end`.

## Where each skill calls this

| Skill | Diagram | File |
|---|---|---|
| `design` | §3 `C4Context`, §5 `C4Container`, §7 deployment; again in the finalize backstop | `sad.md` |
| `sequences` | §6 `sequenceDiagram` per flow; again as the step-8 backstop | `sad.md` |
| `data-model` | `erDiagram` | `data-model.md` |
| `survey` | C4 of what exists / the target baseline | `architecture-map.md` |
| `ux-flows` | one `flowchart` per UI-touching user story | `ux-flows.md` |
| `tasks` | the DAG `flowchart` | `tasks/_epic.md` |
| `roadmap` | the dependency `flowchart` | `docs/roadmap.md` |

Each keeps only a one-line «validate per [`mermaid-check.md`]» pointer; the procedure lives here.
