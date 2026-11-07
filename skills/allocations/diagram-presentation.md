# Diagram presentation — how to confirm a diagram readably (never dump raw Mermaid)

> **Reference-only.** Not a skill. Any skill that asks the user to confirm a Mermaid diagram
> (`design` C4 §3/§5, `sequences` §6 flows, `ux-flows` user flows; others may adopt it) follows this.
> The rule it enforces: **never paste raw Mermaid source into the terminal as the thing to confirm.**
> Raw `sequenceDiagram` / `C4Context` / `flowchart` source is unreadable in a chat box — the user
> can't judge a flow from `participant A as …` lines. Confirm the diagram by a **structured
> plain-language description** of what it shows, while the actual source lands in the file (where
> GitHub, Obsidian or an editor preview renders it) and, only if the user asks, an image.

## Why

A dogfood run pasted raw `sequenceDiagram` blocks as the confirmation prompt. The user can't read arrows-as-text; they approve blind or get frustrated. The fix separates two concerns: the **source** goes where it renders (the `.md` file, an optional image), and the **question** is asked in prose the user can actually evaluate.

This composes with [`mermaid-check.md`](./mermaid-check.md) (which answers «does it parse?») and [`interview-depth.md`](./interview-depth.md) (which answers «ask per-diagram, or proceed?»). This file answers «how do I present it?».

## Procedure (per diagram)

1. **Write the diagram to its file first.** The `sad.md` §6 flow, the §3 C4Context block, the `ux-flows.md` flow, etc. The file is the render surface — GitHub, Obsidian, and editor previews with Mermaid support render it — so writing first means the user can open the rendered view while the question is on screen. Note the line of the ```` ```mermaid ```` fence: that `path:line` goes into the description.
2. **Validate it parses** per [`mermaid-check.md`](./mermaid-check.md) (the structural lint script, plus a full `mmdc` parse when installed). A diagram that doesn't parse is never described or confirmed — fix it first.
3. **Describe it with the template below** — the confirmation is the description, never the source.
4. **Confirm or proceed** per the depth rules below.

## The description template

Every description has the same shape, so the user learns where to look once and scans every later one in seconds:

```
<Diagram name> — <one-line purpose: what this flow/view is for>   (docs/features/<slug>/sad.md:142)
1. <who> <does what> → <to whom>
2. …
Branches:
- If <condition> → <what happens instead>.
- …
```

- **Header line** — the name used in the file heading, a one-line purpose, and the clickable `path:line` of the fence (repo-relative, so the terminal / IDE can open it). Never just «see the file».
- **Numbered steps** — the happy path, one hop per line, at most ~7. If a flow needs more, it is probably two flows — say so in the description instead of writing a wall of steps.
- **Branches** — one bullet for **every** `alt`/`else`/`opt`/error edge / decision node. A branch the description skips is a branch the user can't veto. No branches → write `Branches: none`.
- **Names in the domain's words** — use the participant / screen / system names from the feature's and repo's `CONTEXT.md` Glossary (per-feature wins), never Mermaid ids (`svc`, `db1`) or template placeholders (`<service>`).

Shape per diagram type:

| Diagram | Numbered steps cover | Branches cover |
|---|---|---|
| `sequenceDiagram` (`sequences` §6) | each message hop, caller → callee | every `alt`/`else`/`opt`, timeouts, dead-letter paths |
| `flowchart` user flow (`ux-flows`) | each screen visited, by `SCR-NN` + name | every decision node and error/alt edge |
| `C4Context` (`design` §3) | replace steps with three bullets: **Who uses it** · **What it depends on** · **What it writes to / notifies** | external systems that are optional or degraded |
| `C4Container` (`design` §5) | one line per container: what it does + who calls it | — (write `Branches: none`) |

Example (sequence flow):

```
Read preferences — the member loads their notification settings   (docs/features/prefs/sad.md:142)
1. Member asks for their preferences → Preferences API
2. Preferences API asks Preferences Service → reads Preferences Store
3. Store returns the saved row → API returns it to the member
Branches:
- If no row is saved → the service returns the on-by-default settings instead of an error.
- If the store times out → the API returns «try again» and logs the failure.
```

## Depth governs the ask (per [`interview-depth.md`](./interview-depth.md))

- **easy** → write the diagram + add **one ledger line** per diagram, then **proceed** — no per-diagram question. The line uses the ledger format so the user can veto any diagram in the single ledger review:
  `- A4 · low · flow «Read preferences» = member → API → service → store; no row → defaults; timeout → retry message — because it covers AC-2, AC-4. (docs/features/prefs/sad.md:142)`
  A vetoed diagram becomes a medium-style confirm for that one diagram.
- **medium / hard** → an `AskUserQuestion` confirm per diagram, **batched up to 4 diagrams per call** per [`socratic-loop.md`](./socratic-loop.md) §Batching (write and validate every diagram in the batch first). Each question's text is that diagram's full description (template above); the options are the canonical 4-state actions from [`style.md`](./style.md):
  - **Approve as is** → keep it, move on.
  - **Edit** → take the user's note, regenerate that one diagram, overwrite the block, re-validate, and ask once more (one round — the second answer is final). The re-ask opens with a **`Changed:`** line naming exactly what moved — `Changed: added a «store times out» branch; merged steps 2–3.` — then the full new description, so the user checks the delta instead of re-reading everything.
  - **Save as open question** → remove the block, add the Open-Questions row with owner + due per [`socratic-loop.md`](./socratic-loop.md) (blank owner or due → Drop).
  - **Drop** → remove the block again. If the diagram is **mandatory** (below), re-ask once with a reframed option set; a second Drop escalates to Save as open question with a suggested owner + due and a warning — never a silent gap.

  Ask a diagram **alone** (a batch of one) when it is a follow-up (the Edit re-ask, the owner+due capture) or a C4 view (`design` confirms one section at a time anyway).

The question text is always the **description + `path:line`** — never the raw block. If the user explicitly asks to see the source, show it once; the *default* confirmation channel is the description.

### Which diagrams are mandatory

A diagram is mandatory when dropping it would break coverage that later stages rely on:

- `design` §3 `C4Context` and §5 `C4Container` — always mandatory (one container per declared target surface).
- `sequences` — a flow that is the only coverage for a §4 user story / §5 acceptance criterion.
- `ux-flows` — the flow for a UI-touching §4 user story.

Anything else (an extra illustrative flow, a duplicate view) is optional: Drop removes it with no replacement.

## Images — opt-in, on request only

Images are **not** produced by default: the `.md` file already renders on GitHub and in Obsidian / editor previews, and `mmdc` starts a headless browser on every run. Render only when the user asks («render the diagrams», «I can't see Mermaid here») **and** `mmdc` is on `PATH` — never download it (see [`mermaid-check.md`](./mermaid-check.md)). When `mmdc` is installed, mention the option **once per run** at the first confirm: «Can't see the diagrams rendered? Say "render diagrams" and I'll write SVGs to `docs/features/<slug>/_diagrams/`.»

On request, render **one run per file** (not per diagram), as SVG, into the feature's `_diagrams/` folder:

```bash
d=docs/features/<slug>/_diagrams && mkdir -p "$d" \
  && mmdc -q -e svg -i docs/features/<slug>/sad.md -o "$d/sad.md" 2>&1; rc=$?; rm -f "$d/sad.md"; echo "exit=$rc"
```

`mmdc` with a Markdown input writes one `sad-N.svg` per Mermaid block (N in file order — map N to a diagram with `mermaid_lint.py --list`) plus a rewritten copy of the Markdown, which the command removes. Then:

- **Keep images out of git.** Ensure `.gitignore` contains `docs/features/*/_diagrams/` (add it once, never duplicate it); the `.gitignore` patch rides along in the stage's next commit per [`write-and-commit.md`](./write-and-commit.md). Images are a local viewing aid, regenerated on demand — the committed source of truth is the Mermaid block.
- Add the image path to each affected description's header line: `(docs/features/prefs/sad.md:142 · _diagrams/sad-3.svg)`.
- Non-zero exit → report it per [`mermaid-check.md`](./mermaid-check.md) and carry on with the description alone; a failed render never blocks a confirm.

No `mmdc` and the user asks → say so in one line, with the install hint from [`mermaid-check.md`](./mermaid-check.md), and continue with the description.

## Discipline

- **Never** make the raw Mermaid source the thing the user confirms — that's the anti-pattern this file exists to kill.
- **Write before you ask** — the file is the render surface; asking before writing means there's nothing for the user to open.
- **Describe every branch**, not just the happy path.
- **Validate before you describe** — never describe (or render an image of) a diagram that doesn't parse; fix it per `mermaid-check.md` first.
- **Same template every time** — header with `path:line`, numbered steps, `Branches:`. Consistency is what makes the fourth confirm fast.
- The description is for the user; the source is for the file and downstream stages. Keep the two channels separate.

## Where each skill calls this

| Skill | Diagrams confirmed | Step |
|---|---|---|
| `design` | §3 `C4Context`, §5 `C4Container` (mandatory) | step 6, at those sections |
| `sequences` | §6 `sequenceDiagram`, one per flow | step 6 |
| `ux-flows` | one `flowchart` per UI-touching user story | step 4 |

Validated but **not** confirmed here: `data-model`'s `erDiagram`, `survey`'s C4, `tasks`' DAG and `roadmap`'s dependency flowchart are derived from content the user already confirmed (or from the code), so those skills only run [`mermaid-check.md`](./mermaid-check.md). If one of them ever shows a diagram to the user, it describes it per this file — never raw source.

Each calling skill keeps only a one-line «present per [`diagram-presentation.md`]» pointer; the procedure lives here.
